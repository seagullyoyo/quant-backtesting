import pandas as pd
import numpy as np
from strategy_development import TradingStrategy

# RSI超买超卖策略
class RSIStrategy(TradingStrategy):
    def __init__(self, window=14, overbought=70, oversold=30):
        super().__init__("RSI超买超卖策略", {"窗口": window, "超买阈值": overbought, "超卖阈值": oversold})
        self.window = window
        self.overbought = overbought
        self.oversold = oversold
    
    def generate_signals(self, data):
        """基于RSI指标生成信号"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算日收益率
        delta = data['收盘'].diff()
        
        # 计算上涨、下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算平均上涨、下跌
        avg_gain = gain.rolling(window=self.window, min_periods=1).mean()
        avg_loss = loss.rolling(window=self.window, min_periods=1).mean()
        
        # 计算相对强度
        rs = avg_gain / avg_loss.replace(0, 0.001)  # 避免除以0
        
        # 计算RSI
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # 生成交易信号
        signals[data['RSI'] < self.oversold] = 1  # RSI低于超卖线做多
        signals[data['RSI'] > self.overbought] = -1  # RSI高于超买线做空
        
        return signals

# MACD策略
class MACDStrategy(TradingStrategy):
    def __init__(self, fast=12, slow=26, signal=9):
        super().__init__("MACD策略", {"快线": fast, "慢线": slow, "信号线": signal})
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def generate_signals(self, data):
        """基于MACD指标生成信号"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算快线和慢线的指数移动平均
        data['EMA_fast'] = data['收盘'].ewm(span=self.fast, min_periods=self.fast).mean()
        data['EMA_slow'] = data['收盘'].ewm(span=self.slow, min_periods=self.slow).mean()
        
        # 计算MACD线和信号线
        data['MACD'] = data['EMA_fast'] - data['EMA_slow']
        data['Signal_Line'] = data['MACD'].ewm(span=self.signal, min_periods=self.signal).mean()
        
        # 计算柱状图
        data['Histogram'] = data['MACD'] - data['Signal_Line']
        
        # 生成交易信号 (MACD线上穿信号线做多，下穿做空)
        data['MACD_prev'] = data['MACD'].shift(1)
        data['Signal_prev'] = data['Signal_Line'].shift(1)
        
        # 金叉: 今天MACD线在信号线上方，昨天MACD线在信号线下方
        golden_cross = (data['MACD'] > data['Signal_Line']) & (data['MACD_prev'] < data['Signal_prev'])
        
        # 死叉: 今天MACD线在信号线下方，昨天MACD线在信号线上方
        death_cross = (data['MACD'] < data['Signal_Line']) & (data['MACD_prev'] > data['Signal_prev'])
        
        signals[golden_cross] = 1
        signals[death_cross] = -1
        
        return signals

# 布林带策略
class BollingerBandsStrategy(TradingStrategy):
    def __init__(self, window=20, num_std=2):
        super().__init__("布林带策略", {"窗口": window, "标准差倍数": num_std})
        self.window = window
        self.num_std = num_std
    
    def generate_signals(self, data):
        """基于布林带指标生成信号"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算移动平均线和标准差
        data['SMA'] = data['收盘'].rolling(window=self.window, min_periods=1).mean()
        data['STD'] = data['收盘'].rolling(window=self.window, min_periods=1).std()
        
        # 计算上轨、下轨
        data['Upper_Band'] = data['SMA'] + (data['STD'] * self.num_std)
        data['Lower_Band'] = data['SMA'] - (data['STD'] * self.num_std)
        
        # 生成交易信号
        signals[data['收盘'] < data['Lower_Band']] = 1  # 价格触及下轨做多
        signals[data['收盘'] > data['Upper_Band']] = -1  # 价格触及上轨做空
        
        return signals

# KDJ策略
class KDJStrategy(TradingStrategy):
    def __init__(self, window=9, signal=3, overbought=80, oversold=20):
        super().__init__("KDJ策略", {"窗口": window, "信号线": signal, "超买阈值": overbought, "超卖阈值": oversold})
        self.window = window
        self.signal = signal
        self.overbought = overbought
        self.oversold = oversold
    
    def generate_signals(self, data):
        """基于KDJ指标生成信号"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算过去n天的最高价和最低价
        data['Highest_High'] = data['最高'].rolling(window=self.window).max()
        data['Lowest_Low'] = data['最低'].rolling(window=self.window).min()
        
        # 计算RSV (Raw Stochastic Value)
        data['RSV'] = 100 * ((data['收盘'] - data['Lowest_Low']) / 
                             (data['Highest_High'] - data['Lowest_Low']).replace(0, 0.001))
        
        # 计算K值 (默认初始值为50)
        data['K'] = 50.0
        for i in range(1, len(data)):
            data.loc[data.index[i], 'K'] = (2/3) * data.loc[data.index[i-1], 'K'] + (1/3) * data.loc[data.index[i], 'RSV']
        
        # 计算D值 (默认初始值为50)
        data['D'] = 50.0
        for i in range(1, len(data)):
            data.loc[data.index[i], 'D'] = (2/3) * data.loc[data.index[i-1], 'D'] + (1/3) * data.loc[data.index[i], 'K']
        
        # 计算J值
        data['J'] = 3 * data['K'] - 2 * data['D']
        
        # 生成交易信号 (J值低于超卖线买入，高于超买线卖出)
        signals[data['J'] < self.oversold] = 1
        signals[data['J'] > self.overbought] = -1
        
        return signals

# 量价关系策略
class VolumePriceStrategy(TradingStrategy):
    def __init__(self, price_window=5, volume_window=5, volume_threshold=0.1):
        super().__init__("量价关系策略", {
            "价格窗口": price_window, 
            "成交量窗口": volume_window,
            "成交量增加阈值": volume_threshold
        })
        self.price_window = price_window
        self.volume_window = volume_window
        self.volume_threshold = volume_threshold
    
    def generate_signals(self, data):
        """基于量价关系生成信号"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算价格变动
        data['Price_Change'] = data['收盘'].pct_change()
        
        # 计算成交量变动
        data['Volume_Change'] = data['成交量'].pct_change()
        
        # 计算价格和成交量的移动平均
        data['Price_MA'] = data['收盘'].rolling(window=self.price_window).mean()
        data['Volume_MA'] = data['成交量'].rolling(window=self.volume_window).mean()
        
        # 生成交易信号
        # 1. 价格上涨且成交量显著增加 - 做多
        volume_price_up = (data['Price_Change'] > 0) & (data['Volume_Change'] > self.volume_threshold) & (data['成交量'] > data['Volume_MA'])
        
        # 2. 价格下跌且成交量显著增加 - 做空
        volume_price_down = (data['Price_Change'] < 0) & (data['Volume_Change'] > self.volume_threshold) & (data['成交量'] > data['Volume_MA'])
        
        signals[volume_price_up] = 1
        signals[volume_price_down] = -1
        
        return signals

# 趋势跟踪策略
class TrendFollowingStrategy(TradingStrategy):
    def __init__(self, window=20, threshold=0.03):
        super().__init__("趋势跟踪策略", {"窗口": window, "阈值": threshold})
        self.window = window
        self.threshold = threshold
    
    def generate_signals(self, data):
        """基于价格趋势生成信号"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算移动平均线
        data['MA'] = data['收盘'].rolling(window=self.window).mean()
        
        # 计算价格相对于移动平均线的位置
        data['Relative_Position'] = (data['收盘'] - data['MA']) / data['MA']
        
        # 生成交易信号
        signals[data['Relative_Position'] > self.threshold] = 1  # 价格显著高于均线，做多
        signals[data['Relative_Position'] < -self.threshold] = -1  # 价格显著低于均线，做空
        
        return signals

# 乖离率策略
class BIASStrategy(TradingStrategy):
    def __init__(self, window=20, upper_threshold=0.08, lower_threshold=-0.08):
        super().__init__("乖离率策略", {"窗口": window, "上阈值": upper_threshold, "下阈值": lower_threshold})
        self.window = window
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
    
    def generate_signals(self, data):
        """基于价格与移动平均线的乖离率生成信号"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算移动平均线
        data['MA'] = data['收盘'].rolling(window=self.window).mean()
        
        # 计算乖离率 BIAS = (收盘价 - MA) / MA
        data['BIAS'] = (data['收盘'] - data['MA']) / data['MA']
        
        # 生成交易信号
        signals[data['BIAS'] < self.lower_threshold] = 1  # 乖离率过低，价格有反弹可能，做多
        signals[data['BIAS'] > self.upper_threshold] = -1  # 乖离率过高，价格有回落可能，做空
        
        return signals

# 双均线结合交易量策略
class DualMAVolumeStrategy(TradingStrategy):
    def __init__(self, short_window=5, long_window=20, volume_ratio=1.5):
        super().__init__("双均线结合交易量策略", {"短期窗口": short_window, "长期窗口": long_window, "成交量比例": volume_ratio})
        self.short_window = short_window
        self.long_window = long_window
        self.volume_ratio = volume_ratio
    
    def generate_signals(self, data):
        """结合均线交叉和成交量确认的策略"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算短期和长期移动平均线
        data['短期均线'] = data['收盘'].rolling(window=self.short_window, min_periods=1).mean()
        data['长期均线'] = data['收盘'].rolling(window=self.long_window, min_periods=1).mean()
        
        # 计算均线金叉和死叉
        data['金叉'] = (data['短期均线'] > data['长期均线']) & (data['短期均线'].shift(1) <= data['长期均线'].shift(1))
        data['死叉'] = (data['短期均线'] < data['长期均线']) & (data['短期均线'].shift(1) >= data['长期均线'].shift(1))
        
        # 计算成交量均值
        data['成交量均值'] = data['成交量'].rolling(window=self.long_window).mean()
        
        # 成交量确认条件
        data['成交量放大'] = data['成交量'] > self.volume_ratio * data['成交量均值']
        
        # 生成交易信号 (均线金叉+成交量放大做多，均线死叉+成交量放大做空)
        signals[(data['金叉']) & (data['成交量放大'])] = 1
        signals[(data['死叉']) & (data['成交量放大'])] = -1
        
        return signals 