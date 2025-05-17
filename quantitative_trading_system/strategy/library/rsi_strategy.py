#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSI超买超卖策略
"""
import pandas as pd
import numpy as np

from quantitative_trading_system.strategy.base.strategy_base import StrategyBase
from quantitative_trading_system.data.api.data_api import data_api
from quantitative_trading_system.config.config import STRATEGY_CONFIG


class RSIStrategy(StrategyBase):
    """
    RSI超买超卖策略
    当RSI低于超卖阈值时买入，高于超买阈值时卖出
    """
    
    def __init__(self, name="RSI超买超卖策略", author="Quant Team", description=None):
        """
        初始化RSI策略
        
        Args:
            name (str): 策略名称
            author (str): 策略作者
            description (str, optional): 策略描述
        """
        description = description or "利用RSI指标进行反转交易，当RSI处于超卖区域时买入，超买区域时卖出"
        super().__init__(name=name, author=author, description=description)
        
        # 从配置文件读取默认参数
        rsi_config = STRATEGY_CONFIG.get('rsi', {})
        
        # 设置默认参数
        self.set_parameters(
            symbols=rsi_config.get('symbols', ['000001.SZ']),  # 股票列表
            rsi_period=rsi_config.get('rsi_period', 14),       # RSI计算周期
            overbought=rsi_config.get('overbought', 70),       # 超买阈值
            oversold=rsi_config.get('oversold', 30),           # 超卖阈值
            unit=rsi_config.get('unit', 100)                   # 交易单位
        )
        
        # 策略内部数据
        self.rsi_data = {}  # 存储RSI数据
    
    def initialize(self, context):
        """
        初始化策略
        
        Args:
            context: 策略上下文
        """
        # 获取参数
        self.symbols = self.parameters.get('symbols', ['000001.SZ'])
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.overbought = self.parameters.get('overbought', 70)
        self.oversold = self.parameters.get('oversold', 30)
        self.unit = self.parameters.get('unit', 100)
        
        # 设置上下文中的交易股票
        context['symbols'] = self.symbols
        
        # 预加载历史数据，计算初始RSI
        self._preload_history_data(context)
        
        self.logger.info(f"初始化RSI策略，RSI周期: {self.rsi_period}, "
                       f"超买阈值: {self.overbought}, 超卖阈值: {self.oversold}, "
                       f"交易股票: {self.symbols}")
    
    def _calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100./(1. + rs)

        for i in range(period, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up/down if down != 0 else 0
            rsi[i] = 100. - 100./(1. + rs)
            
        return rsi
    
    def _preload_history_data(self, context):
        """预加载历史数据"""
        # 获取足够长的历史数据，确保能够计算RSI
        start_date = context.get('start_date')
        if start_date:
            # 向前获取足够的历史数据
            from datetime import datetime, timedelta
            lookback_days = self.rsi_period * 3  # 预加载3倍RSI周期的数据
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            lookback_start = (start_dt - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
            
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
                        # 计算RSI
                        if len(symbol_data) > self.rsi_period:
                            prices = symbol_data['close'].values
                            symbol_data['rsi'] = self._calculate_rsi(prices, self.rsi_period)
                            self.rsi_data[symbol] = symbol_data
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
            
            # 更新RSI数据
            if symbol not in self.rsi_data:
                self.rsi_data[symbol] = pd.DataFrame()
            
            # 添加当日数据
            new_row = {
                'date': current_date,
                'close': close_price,
            }
            
            # 将新数据添加到DataFrame
            symbol_data = self.rsi_data[symbol]
            symbol_data = pd.concat([symbol_data, pd.DataFrame([new_row])], ignore_index=True)
            
            # 保留最近的数据
            max_window = self.rsi_period * 3
            if len(symbol_data) > max_window:
                symbol_data = symbol_data.iloc[-max_window:]
            
            # 计算RSI
            if len(symbol_data) > self.rsi_period:
                prices = symbol_data['close'].values
                symbol_data['rsi'] = self._calculate_rsi(prices, self.rsi_period)
                
                # 更新数据
                self.rsi_data[symbol] = symbol_data
                
                # 获取当前RSI值
                current_rsi = symbol_data['rsi'].iloc[-1]
                
                # 生成交易信号
                if pd.notna(current_rsi):
                    # 超卖区域，买入信号
                    if current_rsi < self.oversold:
                        self.signals[symbol] = self.unit
                        self.logger.info(f"生成买入信号: {symbol}, RSI = {current_rsi:.2f}, 交易量: {self.unit}")
                    
                    # 超买区域，卖出信号
                    elif current_rsi > self.overbought:
                        self.signals[symbol] = -self.unit
                        self.logger.info(f"生成卖出信号: {symbol}, RSI = {current_rsi:.2f}, 交易量: {self.unit}")
                    
                    # 无信号
                    else:
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
    创建RSI策略实例
    
    Args:
        name (str, optional): 策略名称
        parameters (dict, optional): 策略参数
        
    Returns:
        RSIStrategy: 策略实例
    """
    strategy = RSIStrategy(name=name)
    if parameters:
        strategy.set_parameters(**parameters)
    return strategy 