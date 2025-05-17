#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测引擎模块
用于在历史数据上模拟交易，评估策略性能
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm

from quantitative_trading_system.utils.logger import get_logger
from quantitative_trading_system.config.config import BACKTEST_CONFIG
from quantitative_trading_system.data.api.data_api import data_api


class BacktestEngine:
    """回测引擎类"""
    
    def __init__(self, strategy, start_date=None, end_date=None, initial_capital=None, 
                commission=None, slippage=None, benchmark=None, data_frequency='daily'):
        """
        初始化回测引擎
        
        Args:
            strategy: 策略对象
            start_date (str, optional): 回测开始日期，格式YYYY-MM-DD
            end_date (str, optional): 回测结束日期，格式YYYY-MM-DD
            initial_capital (float, optional): 初始资金
            commission (float, optional): 交易佣金率
            slippage (float, optional): 滑点率
            benchmark (str, optional): 基准指数代码
            data_frequency (str, optional): 数据频率，'daily', 'minute'等
        """
        self.logger = get_logger(self.__class__.__name__)
        self.strategy = strategy
        
        # 设置回测参数
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.initial_capital = initial_capital or BACKTEST_CONFIG.get('default_initial_capital', 1000000)
        self.commission = commission or BACKTEST_CONFIG.get('default_commission', 0.0003)
        self.slippage = slippage or BACKTEST_CONFIG.get('default_slippage', 0.0001)
        self.benchmark = benchmark or BACKTEST_CONFIG.get('benchmark', '000300.SH')
        self.data_frequency = data_frequency
        
        # 回测状态
        self.context = None
        self.current_date = None
        self.current_datetime = None
        self.current_data = None
        
        # 回测结果
        self.portfolio = None
        self.positions = {}
        self.trades = []
        self.daily_returns = []
        
        self.logger.info(f"初始化回测引擎，策略: {strategy.name}, 回测区间: {start_date} 至 {end_date}")
    
    def initialize(self):
        """初始化回测环境"""
        # 创建上下文对象
        self.context = {
            'strategy': self.strategy,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'current_date': None,
            'current_datetime': None,
            'portfolio': {
                'positions': {},
                'cash': self.initial_capital,
                'total_value': self.initial_capital,
                'returns': [],
                'daily_returns': [],
            },
            'orders': [],
            'trades': [],
            'data_frequency': self.data_frequency,
            'symbols': [],
        }
        
        # 初始化策略
        self.strategy.initialize(self.context)
        self.strategy.is_initialized = True
        
        self.logger.info("回测环境初始化完成")
    
    def run_backtest(self):
        """
        运行回测
        
        Returns:
            dict: 回测结果
        """
        if not self.strategy.is_initialized:
            self.initialize()
        
        # 获取回测日期列表
        dates = self._get_trading_dates()
        if not dates:
            self.logger.error("无法获取交易日历，回测失败")
            return None
        
        self.logger.info(f"开始回测，回测区间: {dates[0]} 至 {dates[-1]}, 共 {len(dates)} 个交易日")
        
        # 获取基准数据
        benchmark_data = self._get_benchmark_data(dates[0], dates[-1])
        
        # 跟踪组合每日价值和收益率
        portfolio_values = [self.initial_capital]
        daily_returns = [0.0]
        
        # 循环每个交易日
        for current_date in tqdm(dates, desc="回测进度"):
            # 更新当前日期
            self.current_date = current_date
            self.context['current_date'] = current_date
            
            # 获取当前交易日数据
            self.current_data = self._get_daily_data(current_date)
            
            # 调用策略的每日开盘前处理
            if self.strategy.is_running:
                self.strategy.before_trading_start(self.context, self.current_data)
            
            # 处理当日数据，生成交易信号
            signals = self.strategy.generate_signals(self.context, self.current_data)
            
            # 执行交易
            if signals:
                self._execute_trades(signals)
            
            # 更新持仓价值
            self._update_portfolio_value()
            
            # 记录每日收益
            portfolio_value = self.context['portfolio']['total_value']
            portfolio_values.append(portfolio_value)
            
            # 计算每日收益率
            daily_return = (portfolio_value / portfolio_values[-2]) - 1 if len(portfolio_values) > 1 else 0
            daily_returns.append(daily_return)
            self.context['portfolio']['daily_returns'].append(daily_return)
            
            # 调用策略的每日收盘后处理
            if self.strategy.is_running:
                self.strategy.after_trading_end(self.context, self.current_data)
        
        # 计算回测结果指标
        results = self._calculate_backtest_metrics(portfolio_values, daily_returns, benchmark_data)
        
        self.logger.info(f"回测完成，最终资产: {portfolio_values[-1]:.2f}, "
                        f"总收益率: {results['total_return']:.2%}, "
                        f"年化收益率: {results['annual_return']:.2%}, "
                        f"最大回撤: {results['max_drawdown']:.2%}, "
                        f"夏普比率: {results['sharpe_ratio']:.2f}")
        
        return results
    
    def _get_trading_dates(self):
        """获取交易日历"""
        # 这里简化处理，获取连续的自然日
        # 实际应使用交易所日历
        from datetime import datetime, timedelta
        
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')
        
        dates = []
        current = start
        while current <= end:
            # 跳过周末
            if current.weekday() < 5:  # 0-4 表示周一至周五
                dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return dates
    
    def _get_daily_data(self, date):
        """获取指定日期的市场数据"""
        symbols = self.context.get('symbols', [])
        if not symbols:
            return {}
        
        try:
            # 使用DataAPI获取市场数据
            result = {}
            for symbol in symbols:
                # 获取单个股票的数据
                data = data_api.get_price(
                    symbols=symbol, 
                    start_date=date, 
                    end_date=date, 
                    freq=self.data_frequency)
                
                if not data.empty:
                    # 将数据添加到结果字典
                    result[symbol] = data.to_dict('records')[0]
                else:
                    # 使用前一日数据填充
                    prev_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
                    prev_data = data_api.get_price(
                        symbols=symbol, 
                        start_date=prev_date, 
                        end_date=prev_date, 
                        freq=self.data_frequency)
                    
                    if not prev_data.empty:
                        result[symbol] = prev_data.to_dict('records')[0]
                    else:
                        result[symbol] = None
            
            return result
            
        except Exception as e:
            self.logger.error(f"获取日期 {date} 的市场数据失败: {str(e)}")
            return {}
    
    def _get_benchmark_data(self, start_date, end_date):
        """获取基准指数数据"""
        try:
            # 使用DataAPI获取基准数据
            benchmark_data = data_api.get_price(
                symbols=self.benchmark, 
                start_date=start_date, 
                end_date=end_date, 
                freq='daily')
            
            if benchmark_data.empty:
                self.logger.warning(f"无法获取基准 {self.benchmark} 的数据")
                return pd.DataFrame()
            
            # 计算基准每日收益率
            benchmark_data['daily_return'] = benchmark_data['close'].pct_change()
            benchmark_data.fillna(0, inplace=True)
            
            return benchmark_data
            
        except Exception as e:
            self.logger.error(f"获取基准数据失败: {str(e)}")
            return pd.DataFrame()
    
    def _execute_trades(self, signals):
        """根据交易信号执行交易"""
        for symbol, signal in signals.items():
            if signal == 0:  # 无操作
                continue
                
            current_price = self._get_current_price(symbol)
            if current_price is None:
                self.logger.warning(f"无法获取 {symbol} 的当前价格，跳过交易")
                continue
            
            # 计算交易价格（考虑滑点）
            if signal > 0:  # 买入
                trade_price = current_price * (1 + self.slippage)
            else:  # 卖出
                trade_price = current_price * (1 - self.slippage)
            
            # 计算可交易的最大数量
            available_cash = self.context['portfolio']['cash']
            max_shares = int(available_cash / (trade_price * (1 + self.commission)))
            
            # 获取当前持仓
            positions = self.context['portfolio']['positions']
            current_position = positions.get(symbol, 0)
            
            # 计算实际交易数量
            if signal > 0:  # 买入
                shares = min(max_shares, abs(signal))
                if shares <= 0:
                    self.logger.warning(f"资金不足，无法买入 {symbol}")
                    continue
            else:  # 卖出
                shares = min(current_position, abs(signal))
                if shares <= 0:
                    self.logger.warning(f"持仓不足，无法卖出 {symbol}")
                    continue
                shares = -shares  # 卖出为负数
            
            # 计算交易金额和手续费
            amount = shares * trade_price
            commission_fee = abs(amount) * self.commission
            
            # 更新持仓和现金
            if symbol not in positions:
                positions[symbol] = 0
            positions[symbol] += shares
            self.context['portfolio']['cash'] -= (amount + commission_fee)
            
            # 记录交易
            trade = {
                'date': self.current_date,
                'symbol': symbol,
                'shares': shares,
                'price': trade_price,
                'amount': amount,
                'commission': commission_fee,
                'type': 'buy' if shares > 0 else 'sell'
            }
            self.context['trades'].append(trade)
            self.trades.append(trade)
            
            self.logger.debug(f"执行交易: {trade}")
    
    def _get_current_price(self, symbol):
        """获取股票当前价格"""
        if self.current_data and symbol in self.current_data:
            data = self.current_data[symbol]
            if data and 'close' in data:
                return data['close']
        return None
    
    def _update_portfolio_value(self):
        """更新投资组合市值"""
        positions = self.context['portfolio']['positions']
        portfolio_value = self.context['portfolio']['cash']
        
        for symbol, shares in list(positions.items()):
            if shares == 0:
                del positions[symbol]
                continue
                
            current_price = self._get_current_price(symbol)
            if current_price is None:
                self.logger.warning(f"无法获取 {symbol} 的当前价格，使用上一次估值")
                continue
                
            position_value = shares * current_price
            portfolio_value += position_value
        
        self.context['portfolio']['total_value'] = portfolio_value
    
    def _calculate_backtest_metrics(self, portfolio_values, daily_returns, benchmark_data):
        """
        计算回测指标
        
        Args:
            portfolio_values (list): 每日组合价值列表
            daily_returns (list): 每日收益率列表
            benchmark_data (DataFrame): 基准指数数据
            
        Returns:
            dict: 回测指标
        """
        # 转换为numpy数组
        portfolio_values = np.array(portfolio_values)
        daily_returns = np.array(daily_returns)
        
        # 计算总收益率
        total_return = (portfolio_values[-1] / portfolio_values[0]) - 1
        
        # 计算年化收益率
        days = len(portfolio_values) - 1
        annual_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0
        
        # 计算波动率（年化）
        volatility = np.std(daily_returns) * np.sqrt(252)
        
        # 计算夏普比率（假设无风险利率为3%）
        risk_free_rate = 0.03
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 计算最大回撤
        max_drawdown = 0
        peak = portfolio_values[0]
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # 计算胜率
        profitable_days = sum(1 for r in daily_returns if r > 0)
        win_rate = profitable_days / len(daily_returns) if len(daily_returns) > 0 else 0
        
        # 计算盈亏比(profit_factor)
        profit_sum = sum(r for r in daily_returns if r > 0)
        loss_sum = abs(sum(r for r in daily_returns if r < 0))
        profit_factor = profit_sum / loss_sum if loss_sum > 0 else float('inf')
        
        # 计算基准收益率（如果有基准数据）
        benchmark_return = 0
        if not benchmark_data.empty and 'close' in benchmark_data.columns:
            benchmark_prices = benchmark_data['close'].values
            benchmark_return = (benchmark_prices[-1] / benchmark_prices[0]) - 1 if len(benchmark_prices) > 1 else 0
        
        # 计算Alpha和Beta（如果有基准数据）
        alpha, beta = 0, 0
        if not benchmark_data.empty and 'daily_return' in benchmark_data.columns:
            # 将基准的每日收益率与策略的每日收益率对齐
            benchmark_returns = benchmark_data['daily_return'].values
            if len(benchmark_returns) == len(daily_returns):
                # 计算Beta
                covariance = np.cov(daily_returns[1:], benchmark_returns[1:])
                if covariance.shape == (2, 2) and covariance[1, 1] != 0:
                    beta = covariance[0, 1] / covariance[1, 1]
                
                # 计算Alpha（年化）
                alpha = annual_return - risk_free_rate - beta * (benchmark_return - risk_free_rate)
        
        # 返回回测指标
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'benchmark_return': benchmark_return,
            'alpha': alpha,
            'beta': beta,
            'portfolio_values': portfolio_values.tolist(),
            'daily_returns': daily_returns.tolist(),
            'final_portfolio_value': portfolio_values[-1],
            'trades': self.trades
        }


def run_backtest(strategy_path, start_date=None, end_date=None, initial_capital=None, 
                benchmark=None, data_frequency='daily'):
    """
    运行回测的便捷函数
    
    Args:
        strategy_path (str): 策略路径或策略对象
        start_date (str, optional): 回测开始日期
        end_date (str, optional): 回测结束日期
        initial_capital (float, optional): 初始资金
        benchmark (str, optional): 基准指数代码
        data_frequency (str, optional): 数据频率
    
    Returns:
        dict: 回测结果
    """
    logger = get_logger("run_backtest")
    
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
        
        # 创建回测引擎
        engine = BacktestEngine(
            strategy=strategy,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            benchmark=benchmark,
            data_frequency=data_frequency
        )
        
        # 运行回测
        results = engine.run_backtest()
        return results
        
    except Exception as e:
        logger.error(f"运行回测失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None 