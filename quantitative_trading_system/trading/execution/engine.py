#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易执行引擎
负责执行交易订单，对接实际交易接口
"""

import time
import threading
from datetime import datetime, time as dt_time

from quantitative_trading_system.utils.logger import get_logger
from quantitative_trading_system.config.config import TRADING_CONFIG


class ExecutionEngine:
    """交易执行引擎"""
    
    def __init__(self, strategy=None, broker=None):
        """
        初始化交易执行引擎
        
        Args:
            strategy: 策略对象
            broker: 券商接口对象
        """
        self.logger = get_logger(self.__class__.__name__)
        self.strategy = strategy
        self.broker = broker
        self.config = TRADING_CONFIG
        
        # 交易状态
        self.is_running = False
        self.trading_thread = None
        self.context = None
        
        # 交易队列
        self.order_queue = []
        self.executed_orders = []
        self.canceled_orders = []
        
        self.logger.info("初始化交易执行引擎")
    
    def start(self):
        """启动交易执行引擎"""
        if self.is_running:
            self.logger.warning("交易执行引擎已经在运行")
            return False
        
        if not self.strategy:
            self.logger.error("未设置策略对象")
            return False
        
        if not self.broker:
            self.logger.error("未设置券商接口对象")
            return False
        
        # 初始化上下文
        self.context = {
            'strategy': self.strategy,
            'broker': self.broker,
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'portfolio': {
                'positions': {},
                'cash': 0,
                'total_value': 0
            },
            'orders': [],
            'trades': []
        }
        
        # 获取账户信息
        self._update_account_info()
        
        # 初始化策略
        if not self.strategy.is_initialized:
            self.strategy.initialize(self.context)
            self.strategy.is_initialized = True
        
        # 设置状态
        self.is_running = True
        self.strategy.is_running = True
        self.strategy.on_strategy_start(self.context)
        
        # 启动交易线程
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        
        self.logger.info("交易执行引擎启动成功")
        return True
    
    def stop(self):
        """停止交易执行引擎"""
        if not self.is_running:
            self.logger.warning("交易执行引擎未运行")
            return False
        
        # 设置状态
        self.is_running = False
        self.strategy.is_running = False
        self.strategy.on_strategy_stop(self.context)
        
        # 等待交易线程结束
        if self.trading_thread and self.trading_thread.is_alive():
            self.trading_thread.join(timeout=5)
        
        # 取消所有未执行的订单
        for order in self.order_queue:
            self._cancel_order(order)
        
        self.logger.info("交易执行引擎已停止")
        return True
    
    def _trading_loop(self):
        """交易循环"""
        self.logger.info("交易循环启动")
        
        while self.is_running:
            try:
                current_time = datetime.now().time()
                
                # 检查是否在交易时段
                if self._is_trading_hours(current_time):
                    # 更新市场数据
                    market_data = self._get_market_data()
                    
                    # 更新上下文
                    self.context['current_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 生成交易信号
                    signals = self.strategy.generate_signals(self.context, market_data)
                    
                    # 处理交易信号
                    if signals:
                        self._process_signals(signals)
                    
                    # 执行订单队列
                    self._execute_order_queue()
                    
                    # 更新账户信息
                    self._update_account_info()
                
                # 每分钟检查一次
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"交易循环发生错误: {str(e)}")
                time.sleep(60)  # 发生错误后等待一分钟再继续
        
        self.logger.info("交易循环结束")
    
    def _is_trading_hours(self, current_time):
        """
        检查是否在交易时段
        
        Args:
            current_time (datetime.time): 当前时间
            
        Returns:
            bool: 是否在交易时段
        """
        # A股交易时段：9:30-11:30, 13:00-15:00
        morning_start = dt_time(9, 30)
        morning_end = dt_time(11, 30)
        afternoon_start = dt_time(13, 0)
        afternoon_end = dt_time(15, 0)
        
        # 检查是否为工作日
        current_date = datetime.now().date()
        weekday = current_date.weekday()
        is_weekday = weekday < 5  # 0-4表示周一至周五
        
        # 检查是否在交易时间
        is_morning_session = morning_start <= current_time <= morning_end
        is_afternoon_session = afternoon_start <= current_time <= afternoon_end
        is_trading_time = is_morning_session or is_afternoon_session
        
        return is_weekday and is_trading_time
    
    def _get_market_data(self):
        """
        获取实时市场数据
        
        Returns:
            dict: 市场数据
        """
        if not self.broker:
            return {}
        
        try:
            # 获取策略中的股票列表
            symbols = self.context.get('symbols', [])
            if not symbols:
                return {}
            
            # 从券商接口获取实时行情
            market_data = self.broker.get_market_data(symbols)
            return market_data
            
        except Exception as e:
            self.logger.error(f"获取市场数据失败: {str(e)}")
            return {}
    
    def _process_signals(self, signals):
        """
        处理交易信号
        
        Args:
            signals (dict): 交易信号字典，格式为 {symbol: signal}
        """
        for symbol, signal in signals.items():
            if signal == 0:  # 无操作
                continue
            
            # 创建订单
            order = {
                'symbol': symbol,
                'shares': abs(signal),
                'direction': 'buy' if signal > 0 else 'sell',
                'order_type': self.config.get('default_order_type', 'limit'),
                'status': 'pending',
                'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'price': None,  # 待填充
                'filled_price': None,
                'filled_shares': 0,
                'commission': 0
            }
            
            # 获取当前市场价格
            market_data = self._get_market_data()
            if symbol in market_data:
                current_price = market_data[symbol].get('last', None)
                if current_price:
                    order['price'] = current_price
            
            # 添加到订单队列
            self.order_queue.append(order)
            self.context['orders'].append(order)
            
            # 回调策略的订单创建事件
            self.strategy.on_order_creation(self.context, order)
            
            self.logger.info(f"创建订单: {symbol}, {order['direction']}, {order['shares']}股")
    
    def _execute_order_queue(self):
        """执行订单队列中的订单"""
        if not self.order_queue:
            return
        
        # 复制一份订单队列，避免在遍历过程中修改
        orders = self.order_queue.copy()
        self.order_queue = []
        
        for order in orders:
            # 执行订单
            result = self._execute_order(order)
            
            if result:
                # 成功执行
                self.executed_orders.append(order)
                
                # 回调策略的订单成交事件
                self.strategy.on_order_filled(self.context, order)
                
                self.logger.info(f"订单执行成功: {order['symbol']}, {order['direction']}, "
                               f"{order['filled_shares']}股, 成交价格: {order['filled_price']}")
            else:
                # 执行失败，重新加入队列
                self.order_queue.append(order)
    
    def _execute_order(self, order):
        """
        执行单个订单
        
        Args:
            order (dict): 订单对象
            
        Returns:
            bool: 是否成功执行
        """
        if not self.broker:
            return False
        
        try:
            # 通过券商接口执行订单
            result = self.broker.execute_order(
                symbol=order['symbol'],
                direction=order['direction'],
                shares=order['shares'],
                order_type=order['order_type'],
                price=order['price']
            )
            
            if result['status'] == 'success':
                # 更新订单信息
                order['status'] = 'filled'
                order['filled_price'] = result['filled_price']
                order['filled_shares'] = result['filled_shares']
                order['commission'] = result['commission']
                order['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 更新持仓信息
                self._update_position(order)
                
                # 记录交易
                trade = {
                    'symbol': order['symbol'],
                    'direction': order['direction'],
                    'shares': order['filled_shares'],
                    'price': order['filled_price'],
                    'amount': order['filled_shares'] * order['filled_price'],
                    'commission': order['commission'],
                    'time': order['update_time']
                }
                self.context['trades'].append(trade)
                
                return True
            else:
                # 执行失败
                order['status'] = 'failed'
                order['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 回调策略的订单拒绝事件
                self.strategy.on_order_rejected(self.context, order)
                
                self.logger.warning(f"订单执行失败: {order['symbol']}, {order['direction']}, "
                                  f"{order['shares']}股, 原因: {result.get('message', '未知')}")
                return False
                
        except Exception as e:
            self.logger.error(f"执行订单时发生错误: {str(e)}")
            return False
    
    def _cancel_order(self, order):
        """
        取消订单
        
        Args:
            order (dict): 订单对象
            
        Returns:
            bool: 是否成功取消
        """
        if not self.broker:
            return False
        
        try:
            # 通过券商接口取消订单
            result = self.broker.cancel_order(order)
            
            if result['status'] == 'success':
                # 更新订单信息
                order['status'] = 'canceled'
                order['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 添加到已取消订单列表
                self.canceled_orders.append(order)
                
                # 回调策略的订单取消事件
                self.strategy.on_order_canceled(self.context, order)
                
                self.logger.info(f"订单取消成功: {order['symbol']}, {order['direction']}, {order['shares']}股")
                return True
            else:
                self.logger.warning(f"订单取消失败: {order['symbol']}, {order['direction']}, "
                                  f"{order['shares']}股, 原因: {result.get('message', '未知')}")
                return False
                
        except Exception as e:
            self.logger.error(f"取消订单时发生错误: {str(e)}")
            return False
    
    def _update_position(self, order):
        """
        更新持仓信息
        
        Args:
            order (dict): 成交的订单对象
        """
        positions = self.context['portfolio']['positions']
        symbol = order['symbol']
        
        # 计算交易金额和手续费
        amount = order['filled_shares'] * order['filled_price']
        commission = order['commission']
        total_cost = amount + commission
        
        # 更新现金
        if order['direction'] == 'buy':
            self.context['portfolio']['cash'] -= total_cost
            # 更新持仓
            if symbol not in positions:
                positions[symbol] = {
                    'shares': 0,
                    'cost': 0,
                    'current_price': order['filled_price'],
                    'market_value': 0
                }
            positions[symbol]['shares'] += order['filled_shares']
            positions[symbol]['cost'] += amount
            positions[symbol]['current_price'] = order['filled_price']
            positions[symbol]['market_value'] = positions[symbol]['shares'] * order['filled_price']
        else:  # sell
            self.context['portfolio']['cash'] += amount - commission
            # 更新持仓
            if symbol in positions:
                positions[symbol]['shares'] -= order['filled_shares']
                # 如果卖空了，更新成本为0
                if positions[symbol]['shares'] <= 0:
                    positions[symbol]['cost'] = 0
                positions[symbol]['current_price'] = order['filled_price']
                positions[symbol]['market_value'] = positions[symbol]['shares'] * order['filled_price']
                # 如果持仓为0，从持仓字典中删除
                if positions[symbol]['shares'] == 0:
                    del positions[symbol]
    
    def _update_account_info(self):
        """更新账户信息"""
        if not self.broker:
            return
        
        try:
            # 获取账户信息
            account_info = self.broker.get_account_info()
            
            # 更新上下文中的账户信息
            self.context['portfolio']['cash'] = account_info['cash']
            
            # 更新持仓
            positions = {}
            for symbol, position in account_info['positions'].items():
                positions[symbol] = {
                    'shares': position['shares'],
                    'cost': position['cost'],
                    'current_price': position['current_price'],
                    'market_value': position['market_value']
                }
            self.context['portfolio']['positions'] = positions
            
            # 计算总资产
            total_value = account_info['cash']
            for symbol, position in positions.items():
                total_value += position['market_value']
            self.context['portfolio']['total_value'] = total_value
            
            self.logger.debug(f"更新账户信息成功，现金: {account_info['cash']:.2f}, 总资产: {total_value:.2f}")
            
        except Exception as e:
            self.logger.error(f"更新账户信息失败: {str(e)}")


# 启动实盘交易的便捷函数
def start_live_trading(strategy_path, broker=None):
    """
    启动实盘交易
    
    Args:
        strategy_path (str): 策略路径或策略对象
        broker: 券商接口对象
    
    Returns:
        ExecutionEngine: 执行引擎对象
    """
    logger = get_logger("start_live_trading")
    
    try:
        # 加载策略
        if isinstance(strategy_path, str):
            if os.path.isfile(strategy_path):
                # 从文件加载策略
                from quantitative_trading_system.strategy.base.strategy_base import StrategyBase
                strategy = StrategyBase.load(strategy_path)
                if not strategy:
                    logger.error(f"加载策略失败: {strategy_path}")
                    return None
            else:
                # 从模块加载策略
                import importlib
                import inspect
                
                try:
                    module_path, class_name = strategy_path.rsplit('.', 1)
                    module = importlib.import_module(module_path)
                    strategy_class = getattr(module, class_name)
                    strategy = strategy_class()
                except (ValueError, ImportError, AttributeError) as e:
                    logger.error(f"加载策略失败: {str(e)}")
                    return None
        else:
            # 直接使用传入的策略对象
            strategy = strategy_path
        
        # 检查是否有券商接口对象
        if not broker:
            # 创建模拟券商接口
            from quantitative_trading_system.trading.adapter.simulator import SimulatedBroker
            broker = SimulatedBroker()
            logger.warning("未提供券商接口对象，使用模拟券商接口")
        
        # 创建执行引擎
        engine = ExecutionEngine(strategy=strategy, broker=broker)
        
        # 启动引擎
        if engine.start():
            logger.info(f"成功启动实盘交易，策略: {strategy.name}")
            return engine
        else:
            logger.error("启动实盘交易失败")
            return None
        
    except Exception as e:
        logger.error(f"启动实盘交易时发生错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None 