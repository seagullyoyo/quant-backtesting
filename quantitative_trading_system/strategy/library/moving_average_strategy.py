#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动平均线交叉策略
"""
import pandas as pd
import numpy as np

from quantitative_trading_system.strategy.base.strategy_base import StrategyBase
from quantitative_trading_system.data.api.data_api import data_api
from quantitative_trading_system.config.config import STRATEGY_CONFIG


class MovingAverageStrategy(StrategyBase):
    """
    移动平均线交叉策略
    当短期移动平均线上穿长期移动平均线时买入，下穿时卖出
    """
    
    def __init__(self, name="移动平均线交叉策略", author="Quant Team", description=None):
        """
        初始化移动平均线交叉策略
        
        Args:
            name (str): 策略名称
            author (str): 策略作者
            description (str, optional): 策略描述
        """
        description = description or "当短期移动平均线上穿长期移动均线时买入，下穿时卖出"
        super().__init__(name=name, author=author, description=description)
        
        # 从配置文件读取默认参数
        ma_config = STRATEGY_CONFIG.get('moving_average', {})
        
        # 设置默认参数
        self.set_parameters(
            symbols=ma_config.get('symbols', ['000001.SZ']),  # 股票列表
            short_window=ma_config.get('short_window', 5),   # 短期窗口
            long_window=ma_config.get('long_window', 20),    # 长期窗口
            unit=ma_config.get('unit', 100)                  # 交易单位
        )
        
        # 策略内部数据
        self.ma_data = {}  # 存储MA数据
    
    def initialize(self, context):
        """
        初始化策略
        
        Args:
            context: 策略上下文
        """
        # 获取参数
        self.symbols = self.parameters.get('symbols', ['000001.SZ'])
        self.short_window = self.parameters.get('short_window', 5)
        self.long_window = self.parameters.get('long_window', 20)
        self.unit = self.parameters.get('unit', 100)
        
        # 设置上下文中的交易股票
        context['symbols'] = self.symbols
        
        # 预加载历史数据，计算初始的均线
        self._preload_history_data(context)
        
        self.logger.info(f"初始化移动平均线交叉策略，短期窗口: {self.short_window}, "
                       f"长期窗口: {self.long_window}, 交易股票: {self.symbols}")
    
    def _preload_history_data(self, context):
        """预加载历史数据"""
        # 获取足够长的历史数据，确保能够计算长期移动平均线
        start_date = context.get('start_date')
        if start_date:
            # 向前获取足够的历史数据
            from datetime import datetime, timedelta
            lookback_days = self.long_window * 2  # 预加载2倍长期窗口的数据
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
                        symbol_data['short_ma'] = symbol_data['close'].rolling(window=self.short_window).mean()
                        symbol_data['long_ma'] = symbol_data['close'].rolling(window=self.long_window).mean()
                        self.ma_data[symbol] = symbol_data
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
            
            # 更新移动平均线数据
            if symbol not in self.ma_data:
                self.ma_data[symbol] = pd.DataFrame()
            
            # 添加当日数据
            new_row = {
                'date': current_date,
                'close': close_price,
            }
            
            # 将新数据添加到DataFrame
            symbol_data = self.ma_data[symbol]
            symbol_data = pd.concat([symbol_data, pd.DataFrame([new_row])], ignore_index=True)
            
            # 保留最近的数据
            max_window = max(self.short_window, self.long_window) * 2
            if len(symbol_data) > max_window:
                symbol_data = symbol_data.iloc[-max_window:]
            
            # 计算移动平均线
            symbol_data['short_ma'] = symbol_data['close'].rolling(window=self.short_window).mean()
            symbol_data['long_ma'] = symbol_data['close'].rolling(window=self.long_window).mean()
            
            # 更新数据
            self.ma_data[symbol] = symbol_data
            
            # 生成交易信号
            if len(symbol_data) >= self.long_window + 1:  # 确保有足够的数据计算信号
                # 获取当前和前一个时间点的均线值
                current_short_ma = symbol_data['short_ma'].iloc[-1]
                current_long_ma = symbol_data['long_ma'].iloc[-1]
                prev_short_ma = symbol_data['short_ma'].iloc[-2]
                prev_long_ma = symbol_data['long_ma'].iloc[-2]
                
                # 检查是否有效（非NaN）
                if (pd.notna(current_short_ma) and pd.notna(current_long_ma) and 
                    pd.notna(prev_short_ma) and pd.notna(prev_long_ma)):
                    
                    # 金叉：短期均线上穿长期均线
                    if prev_short_ma <= prev_long_ma and current_short_ma > current_long_ma:
                        self.signals[symbol] = self.unit
                        self.logger.info(f"生成买入信号: {symbol}, 金叉, 交易量: {self.unit}")
                    
                    # 死叉：短期均线下穿长期均线
                    elif prev_short_ma >= prev_long_ma and current_short_ma < current_long_ma:
                        self.signals[symbol] = -self.unit
                        self.logger.info(f"生成卖出信号: {symbol}, 死叉, 交易量: {self.unit}")
                    
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
        
        # 打印当日持仓和市值
        positions = context['portfolio']['positions']
        total_value = context['portfolio']['total_value']
        cash = context['portfolio']['cash']
        
        self.logger.info(f"收盘后持仓: {positions}, 现金: {cash:.2f}, 总市值: {total_value:.2f}")


# 策略工厂函数
def create_strategy(name=None, parameters=None):
    """
    创建移动平均线交叉策略的工厂函数
    
    Args:
        name (str, optional): 策略名称
        parameters (dict, optional): 策略参数
    
    Returns:
        MovingAverageStrategy: 策略实例
    """
    strategy = MovingAverageStrategy(name=name or "移动平均线交叉策略")
    
    if parameters:
        strategy.set_parameters(**parameters)
    
    return strategy 