#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟券商接口
用于模拟实盘交易环境
"""

import random
import pandas as pd
from datetime import datetime

from quantitative_trading_system.utils.logger import get_logger
from quantitative_trading_system.data.api.data_api import data_api


class SimulatedBroker:
    """模拟券商接口类"""
    
    def __init__(self, initial_capital=1000000, commission=0.0003, slippage=0.0001):
        """
        初始化模拟券商接口
        
        Args:
            initial_capital (float): 初始资金
            commission (float): 佣金率
            slippage (float): 滑点率
        """
        self.logger = get_logger(self.__class__.__name__)
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # 账户信息
        self.cash = initial_capital
        self.positions = {}
        self.orders = []
        self.trades = []
        
        self.logger.info(f"初始化模拟券商接口，初始资金: {initial_capital}")
    
    def get_account_info(self):
        """
        获取账户信息
        
        Returns:
            dict: 账户信息
        """
        # 计算总资产
        total_value = self.cash
        for symbol, position in self.positions.items():
            total_value += position['market_value']
        
        return {
            'cash': self.cash,
            'positions': self.positions,
            'total_value': total_value
        }
    
    def get_market_data(self, symbols):
        """
        获取市场数据
        
        Args:
            symbols (list): 股票代码列表
            
        Returns:
            dict: 市场数据
        """
        try:
            # 使用DataAPI获取最新数据
            today = datetime.now().strftime('%Y-%m-%d')
            df = data_api.get_price(symbols=symbols, end_date=today, freq='daily')
            
            if df.empty:
                self.logger.warning(f"无法获取市场数据: {symbols}")
                return {}
            
            # 构建市场数据字典
            market_data = {}
            for symbol in symbols:
                symbol_data = df[df['symbol'] == symbol]
                if not symbol_data.empty:
                    latest_data = symbol_data.iloc[-1]
                    market_data[symbol] = {
                        'open': latest_data['open'],
                        'high': latest_data['high'],
                        'low': latest_data['low'],
                        'close': latest_data['close'],
                        'volume': latest_data['volume'],
                        'last': latest_data['close'],  # 使用收盘价作为最新价
                        'bid': latest_data['close'] * 0.999,  # 模拟买一价
                        'ask': latest_data['close'] * 1.001   # 模拟卖一价
                    }
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"获取市场数据失败: {str(e)}")
            return {}
    
    def execute_order(self, symbol, direction, shares, order_type='limit', price=None):
        """
        执行订单
        
        Args:
            symbol (str): 股票代码
            direction (str): 交易方向，'buy'或'sell'
            shares (int): 交易数量
            order_type (str, optional): 订单类型. Defaults to 'limit'.
            price (float, optional): 交易价格. Defaults to None.
            
        Returns:
            dict: 订单执行结果
        """
        try:
            # 获取市场数据
            market_data = self.get_market_data([symbol])
            if not market_data or symbol not in market_data:
                return {
                    'status': 'failed',
                    'message': f"无法获取 {symbol} 的市场数据"
                }
            
            # 获取市场价格
            symbol_data = market_data[symbol]
            market_price = symbol_data['last']
            
            # 确定成交价格（考虑滑点）
            if direction == 'buy':
                executed_price = price or symbol_data['ask']
                executed_price *= (1 + self.slippage)  # 买入价格上浮
            else:  # sell
                executed_price = price or symbol_data['bid']
                executed_price *= (1 - self.slippage)  # 卖出价格下浮
            
            # 计算成交金额和手续费
            amount = shares * executed_price
            commission_fee = amount * self.commission
            
            # 验证资金是否足够（买入）
            if direction == 'buy' and amount + commission_fee > self.cash:
                return {
                    'status': 'failed',
                    'message': f"资金不足，需要 {amount + commission_fee}，可用 {self.cash}"
                }
            
            # 验证持仓是否足够（卖出）
            if direction == 'sell':
                position = self.positions.get(symbol, {'shares': 0})
                if shares > position['shares']:
                    return {
                        'status': 'failed',
                        'message': f"持仓不足，需要 {shares}，可用 {position['shares']}"
                    }
            
            # 更新资金和持仓
            if direction == 'buy':
                self.cash -= (amount + commission_fee)
                
                # 更新持仓
                if symbol not in self.positions:
                    self.positions[symbol] = {
                        'shares': 0,
                        'cost': 0,
                        'current_price': executed_price,
                        'market_value': 0
                    }
                
                self.positions[symbol]['shares'] += shares
                self.positions[symbol]['cost'] += amount
                self.positions[symbol]['current_price'] = executed_price
                self.positions[symbol]['market_value'] = self.positions[symbol]['shares'] * executed_price
                
            else:  # sell
                self.cash += (amount - commission_fee)
                
                # 更新持仓
                self.positions[symbol]['shares'] -= shares
                if self.positions[symbol]['shares'] <= 0:
                    self.positions[symbol]['cost'] = 0
                self.positions[symbol]['current_price'] = executed_price
                self.positions[symbol]['market_value'] = self.positions[symbol]['shares'] * executed_price
                
                # 如果持仓为0，从持仓字典中删除
                if self.positions[symbol]['shares'] == 0:
                    del self.positions[symbol]
            
            # 记录交易
            trade = {
                'symbol': symbol,
                'direction': direction,
                'shares': shares,
                'price': executed_price,
                'amount': amount,
                'commission': commission_fee,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.trades.append(trade)
            
            # 生成订单执行结果
            result = {
                'status': 'success',
                'filled_price': executed_price,
                'filled_shares': shares,
                'commission': commission_fee,
                'trade': trade
            }
            
            self.logger.info(f"执行订单成功: {symbol}, {direction}, {shares}股, 价格: {executed_price}")
            return result
            
        except Exception as e:
            self.logger.error(f"执行订单失败: {str(e)}")
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    def cancel_order(self, order):
        """
        取消订单
        
        Args:
            order (dict): 订单对象
            
        Returns:
            dict: 取消结果
        """
        # 模拟取消订单
        return {
            'status': 'success',
            'message': '订单已取消'
        } 