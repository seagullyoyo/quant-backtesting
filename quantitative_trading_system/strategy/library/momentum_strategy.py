#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动量策略
"""
import pandas as pd
import numpy as np

from quantitative_trading_system.strategy.base.strategy_base import StrategyBase
from quantitative_trading_system.data.api.data_api import data_api
from quantitative_trading_system.config.config import STRATEGY_CONFIG


class MomentumStrategy(StrategyBase):
    """
    动量策略
    根据价格趋势进行交易，价格上涨动量强时买入，下跌动量强时卖出
    """
    
    def __init__(self, name="动量策略", author="Quant Team", description=None):
        """
        初始化动量策略
        
        Args:
            name (str): 策略名称
            author (str): 策略作者
            description (str, optional): 策略描述
        """
        description = description or "利用价格动量进行交易，买入过去表现强势的股票，卖出过去表现弱势的股票"
        super().__init__(name=name, author=author, description=description)
        
        # 从配置文件读取默认参数
        momentum_config = STRATEGY_CONFIG.get('momentum', {})
        
        # 设置默认参数
        self.set_parameters(
            symbols=momentum_config.get('symbols', ['000001.SZ']),           # 股票列表
            lookback_period=momentum_config.get('lookback_period', 60),      # 回溯周期
            holding_period=momentum_config.get('holding_period', 20),        # 持有周期
            momentum_threshold=momentum_config.get('momentum_threshold', 5), # 动量阈值（百分比）
            unit=momentum_config.get('unit', 100)                            # 交易单位
        )
        
        # 策略内部数据
        self.momentum_data = {}  # 存储动量数据
        self.holding_days = {}   # 当前持有天数
    
    def initialize(self, context):
        """
        初始化策略
        
        Args:
            context: 策略上下文
        """
        # 获取参数
        self.symbols = self.parameters.get('symbols', ['000001.SZ'])
        self.lookback_period = self.parameters.get('lookback_period', 60)
        self.holding_period = self.parameters.get('holding_period', 20)
        self.momentum_threshold = self.parameters.get('momentum_threshold', 5)
        self.unit = self.parameters.get('unit', 100)
        
        # 设置上下文中的交易股票
        context['symbols'] = self.symbols
        
        # 初始化持有天数
        for symbol in self.symbols:
            self.holding_days[symbol] = 0
        
        # 预加载历史数据，计算初始动量
        self._preload_history_data(context)
        
        self.logger.info(f"初始化动量策略，回溯周期: {self.lookback_period}, "
                       f"持有周期: {self.holding_period}, "
                       f"动量阈值: {self.momentum_threshold}%, 交易股票: {self.symbols}")
    
    def _calculate_momentum(self, prices, lookback_period=60):
        """计算价格动量"""
        if len(prices) < lookback_period:
            return None
            
        # 计算动量（当前价格与lookback_period天前价格相比的百分比变化）
        momentum = np.zeros_like(prices)
        momentum[:lookback_period] = np.nan
        
        for i in range(lookback_period, len(prices)):
            if prices[i-lookback_period] > 0:  # 避免除以零
                momentum[i] = ((prices[i] / prices[i-lookback_period]) - 1) * 100
            else:
                momentum[i] = 0
                
        return momentum
    
    def _preload_history_data(self, context):
        """预加载历史数据"""
        # 获取足够长的历史数据，确保能够计算动量
        start_date = context.get('start_date')
        if start_date:
            # 向前获取足够的历史数据
            from datetime import datetime, timedelta
            lookback_days = self.lookback_period * 2  # 预加载2倍回溯周期的数据
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            lookback_start = (start_dt - timedelta(days=lookback_days*2)).strftime('%Y-%m-%d')  # 因为交易日非连续
            
            # 获取历史数据
            for symbol in self.symbols:
                history_data = data_api.get_price(
                    symbols=symbol,
                    start_date=lookback_start,
                    end_date=start_date,
                    freq='daily'
                )
                
                if not history_data.empty:
                    # 复制数据并排序
                    symbol_data = history_data.copy()
                    if not symbol_data.empty:
                        symbol_data.sort_values('date', inplace=True)
                        # 计算动量
                        if len(symbol_data) > self.lookback_period:
                            prices = symbol_data['close'].values
                            symbol_data['momentum'] = self._calculate_momentum(prices, self.lookback_period)
                            self.momentum_data[symbol] = symbol_data
                            self.logger.debug(f"预加载 {symbol} 的历史数据，记录数: {len(symbol_data)}")
    
    def handle_data(self, context, data):
        """
        处理行情数据，生成交易信号
        
        Args:
            context: 策略上下文
            data: 当前市场数据
        """
        if not data or isinstance(data, pd.DataFrame) and data.empty:
            self.logger.warning("当前无市场数据")
            return
        
        current_date = context.get('current_date')
        self.logger.debug(f"处理 {current_date} 的市场数据")
        
        # 初始化信号字典
        self.signals = {}
        
        # 遍历每只股票
        for symbol in self.symbols:
            if symbol not in data:
                self.logger.warning(f"股票 {symbol} 当日无数据")
                continue
            
            # 获取当日数据
            daily_data = data[symbol]
            if not daily_data or 'close' not in daily_data:
                continue
            
            # 获取收盘价
            close_price = daily_data['close']
            
            # 更新动量数据
            if symbol not in self.momentum_data:
                self.momentum_data[symbol] = pd.DataFrame()
            
            # 添加当日数据
            new_row = {
                'date': current_date,
                'close': close_price,
            }
            
            # 将新数据添加到DataFrame
            symbol_data = self.momentum_data[symbol]
            symbol_data = pd.concat([symbol_data, pd.DataFrame([new_row])], ignore_index=True)
            
            # 保留最近的数据
            max_window = self.lookback_period * 3
            if len(symbol_data) > max_window:
                symbol_data = symbol_data.iloc[-max_window:]
            
            # 计算动量
            if len(symbol_data) > self.lookback_period:
                prices = symbol_data['close'].values
                symbol_data['momentum'] = self._calculate_momentum(prices, self.lookback_period)
                
                # 更新数据
                self.momentum_data[symbol] = symbol_data
                
                # 获取当前动量值
                current_momentum = symbol_data['momentum'].iloc[-1]
                
                # 更新持有天数
                if symbol in self.holding_days:
                    if context.get('portfolio', {}).get('positions', {}).get(symbol, 0) > 0:
                        self.holding_days[symbol] += 1
                    else:
                        self.holding_days[symbol] = 0
                
                # 生成交易信号
                if pd.notna(current_momentum):
                    # 持有期已满，考虑平仓
                    current_position = context.get('portfolio', {}).get('positions', {}).get(symbol, 0)
                    
                    if current_position > 0 and self.holding_days[symbol] >= self.holding_period:
                        self.signals[symbol] = -self.unit
                        self.holding_days[symbol] = 0
                        self.logger.info(f"持有期满平仓: {symbol}, 持有天数: {self.holding_days[symbol]}, 交易量: {-self.unit}")
                    # 强劲上涨动量，买入信号
                    elif current_momentum > self.momentum_threshold and current_position == 0:
                        self.signals[symbol] = self.unit
                        self.logger.info(f"生成买入信号: {symbol}, 动量 = {current_momentum:.2f}%, 交易量: {self.unit}")
                    
                    # 强劲下跌动量，卖出信号
                    elif current_momentum < -self.momentum_threshold and current_position > 0:
                        self.signals[symbol] = -self.unit
                        self.holding_days[symbol] = 0
                        self.logger.info(f"生成卖出信号: {symbol}, 动量 = {current_momentum:.2f}%, 交易量: {-self.unit}")
                    
                    # 无信号或持有中
                    elif current_position == 0:
                        self.signals[symbol] = 0
    
    def before_trading_start(self, context, data):
        """
        每日开盘前处理
        
        Args:
            context: 策略上下文
            data: 当前市场数据
        """
        current_date = context.get('current_date')
        self.logger.debug(f"开盘前准备: {current_date}")
    
    def after_trading_end(self, context, data):
        """
        每日收盘后处理
        
        Args:
            context: 策略上下文
            data: 当前市场数据
        """
        current_date = context.get('current_date')
        self.logger.debug(f"收盘后处理: {current_date}")

def create_strategy(name=None, parameters=None):
    """
    创建动量策略实例
    
    Args:
        name (str, optional): 策略名称
        parameters (dict, optional): 策略参数
        
    Returns:
        MomentumStrategy: 策略实例
    """
    strategy = MomentumStrategy(name=name)
    if parameters:
        strategy.set_parameters(**parameters)
    return strategy 