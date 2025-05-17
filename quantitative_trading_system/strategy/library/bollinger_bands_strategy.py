#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布林带策略
"""
import pandas as pd
import numpy as np

from quantitative_trading_system.strategy.base.strategy_base import StrategyBase
from quantitative_trading_system.data.api.data_api import data_api
from quantitative_trading_system.config.config import STRATEGY_CONFIG


class BollingerBandsStrategy(StrategyBase):
    """
    布林带策略
    当价格突破下轨时买入，突破上轨时卖出
    """
    
    def __init__(self, name="布林带策略", author="Quant Team", description=None):
        """
        初始化布林带策略
        
        Args:
            name (str): 策略名称
            author (str): 策略作者
            description (str, optional): 策略描述
        """
        description = description or "利用布林带进行交易，当价格突破下轨时买入，突破上轨时卖出"
        super().__init__(name=name, author=author, description=description)
        
        # 从配置文件读取默认参数
        bb_config = STRATEGY_CONFIG.get('bollinger_bands', {})
        
        # 设置默认参数
        self.set_parameters(
            symbols=bb_config.get('symbols', ['000001.SZ']),  # 股票列表
            window=bb_config.get('window', 20),               # 移动平均窗口
            num_std=bb_config.get('num_std', 2.0),            # 标准差倍数
            unit=bb_config.get('unit', 100)                   # 交易单位
        )
        
        # 策略内部数据
        self.bollinger_data = {}  # 存储布林带数据
    
    def initialize(self, context):
        """
        初始化策略
        
        Args:
            context: 策略上下文
        """
        # 获取参数
        self.symbols = self.parameters.get('symbols', ['000001.SZ'])
        self.window = self.parameters.get('window', 20)
        self.num_std = self.parameters.get('num_std', 2.0)
        self.unit = self.parameters.get('unit', 100)
        
        # 设置上下文中的交易股票
        context['symbols'] = self.symbols
        
        # 预加载历史数据，计算初始布林带
        self._preload_history_data(context)
        
        self.logger.info(f"初始化布林带策略，窗口: {self.window}, "
                       f"标准差倍数: {self.num_std}, 交易股票: {self.symbols}")
    
    def _calculate_bollinger_bands(self, prices, window=20, num_std=2.0):
        """计算布林带指标"""
        if len(prices) < window:
            return None, None, None
            
        # 计算移动平均线
        middle_band = pd.Series(prices).rolling(window=window).mean().values
        
        # 计算标准差
        rolling_std = pd.Series(prices).rolling(window=window).std().values
        
        # 计算上轨和下轨
        upper_band = middle_band + (rolling_std * num_std)
        lower_band = middle_band - (rolling_std * num_std)
        
        return middle_band, upper_band, lower_band
    
    def _preload_history_data(self, context):
        """预加载历史数据"""
        # 获取足够长的历史数据，确保能够计算布林带
        start_date = context.get('start_date')
        if start_date:
            # 向前获取足够的历史数据
            from datetime import datetime, timedelta
            lookback_days = self.window * 2  # 预加载2倍窗口的数据
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
                        # 计算布林带
                        if len(symbol_data) > self.window:
                            prices = symbol_data['close'].values
                            middle, upper, lower = self._calculate_bollinger_bands(
                                prices, self.window, self.num_std
                            )
                            if middle is not None:
                                symbol_data['middle_band'] = middle
                                symbol_data['upper_band'] = upper
                                symbol_data['lower_band'] = lower
                                self.bollinger_data[symbol] = symbol_data
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
            
            # 更新布林带数据
            if symbol not in self.bollinger_data:
                self.bollinger_data[symbol] = pd.DataFrame()
            
            # 添加当日数据
            new_row = {
                'date': current_date,
                'close': close_price,
            }
            
            # 将新数据添加到DataFrame
            symbol_data = self.bollinger_data[symbol]
            symbol_data = pd.concat([symbol_data, pd.DataFrame([new_row])], ignore_index=True)
            
            # 保留最近的数据
            max_window = self.window * 3
            if len(symbol_data) > max_window:
                symbol_data = symbol_data.iloc[-max_window:]
            
            # 计算布林带
            if len(symbol_data) > self.window:
                prices = symbol_data['close'].values
                middle, upper, lower = self._calculate_bollinger_bands(
                    prices, self.window, self.num_std
                )
                
                if middle is not None:
                    symbol_data['middle_band'] = middle
                    symbol_data['upper_band'] = upper
                    symbol_data['lower_band'] = lower
                    
                    # 更新数据
                    self.bollinger_data[symbol] = symbol_data
                    
                    # 获取当前值
                    current_price = symbol_data['close'].iloc[-1]
                    current_upper = symbol_data['upper_band'].iloc[-1]
                    current_lower = symbol_data['lower_band'].iloc[-1]
                    
                    # 生成交易信号
                    if pd.notna(current_upper) and pd.notna(current_lower):
                        # 价格突破下轨，买入信号
                        if current_price <= current_lower:
                            self.signals[symbol] = self.unit
                            self.logger.info(f"生成买入信号: {symbol}, 价格={current_price:.2f}，下轨={current_lower:.2f}, 交易量: {self.unit}")
                        
                        # 价格突破上轨，卖出信号
                        elif current_price >= current_upper:
                            self.signals[symbol] = -self.unit
                            self.logger.info(f"生成卖出信号: {symbol}, 价格={current_price:.2f}，上轨={current_upper:.2f}, 交易量: {self.unit}")
                        
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
    创建布林带策略实例
    
    Args:
        name (str, optional): 策略名称
        parameters (dict, optional): 策略参数
        
    Returns:
        BollingerBandsStrategy: 策略实例
    """
    strategy = BollingerBandsStrategy(name=name)
    if parameters:
        strategy.set_parameters(**parameters)
    return strategy 