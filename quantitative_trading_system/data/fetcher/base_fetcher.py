#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据抓取器基类
"""
import abc
import logging
from datetime import datetime

from quantitative_trading_system.utils.logger import get_logger


class BaseFetcher(abc.ABC):
    """数据抓取器基类，定义数据抓取的标准接口"""
    
    def __init__(self, data_source=None):
        """
        初始化数据抓取器
        
        Args:
            data_source (str, optional): 数据源名称. Defaults to None.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.data_source = data_source
        self.logger.info(f"初始化数据抓取器: {self.__class__.__name__}, 数据源: {data_source}")
    
    @abc.abstractmethod
    def fetch_data(self, symbols, start_date=None, end_date=None, freq='daily'):
        """
        抓取数据的抽象方法，子类必须实现
        
        Args:
            symbols (list): 股票代码列表
            start_date (str, optional): 开始日期，格式YYYY-MM-DD. Defaults to None.
            end_date (str, optional): 结束日期，格式YYYY-MM-DD. Defaults to None.
            freq (str, optional): 数据频率，如daily, minute, tick. Defaults to 'daily'.
            
        Returns:
            pandas.DataFrame: 抓取的数据
        """
        pass
    
    def validate_params(self, symbols, start_date=None, end_date=None, freq='daily'):
        """
        验证参数合法性
        
        Args:
            symbols (list): 股票代码列表
            start_date (str, optional): 开始日期，格式YYYY-MM-DD. Defaults to None.
            end_date (str, optional): 结束日期，格式YYYY-MM-DD. Defaults to None.
            freq (str, optional): 数据频率，如daily, minute, tick. Defaults to 'daily'.
            
        Returns:
            bool: 参数是否合法
        """
        # 验证股票代码列表
        if not symbols:
            self.logger.error("股票代码列表不能为空")
            return False
        
        # 验证日期格式
        date_format = "%Y-%m-%d"
        if start_date:
            try:
                datetime.strptime(start_date, date_format)
            except ValueError:
                self.logger.error(f"开始日期格式不正确: {start_date}, 应为YYYY-MM-DD")
                return False
        
        if end_date:
            try:
                datetime.strptime(end_date, date_format)
            except ValueError:
                self.logger.error(f"结束日期格式不正确: {end_date}, 应为YYYY-MM-DD")
                return False
        
        # 验证日期先后顺序
        if start_date and end_date:
            if datetime.strptime(start_date, date_format) > datetime.strptime(end_date, date_format):
                self.logger.error(f"开始日期 {start_date} 不能晚于结束日期 {end_date}")
                return False
        
        # 验证数据频率
        valid_freqs = ['daily', 'weekly', 'monthly', '1min', '5min', '15min', '30min', '60min', 'tick']
        if freq not in valid_freqs:
            self.logger.error(f"不支持的数据频率: {freq}, 支持的频率有: {valid_freqs}")
            return False
        
        return True
    
    def preprocess_data(self, data):
        """
        对抓取的数据进行预处理
        
        Args:
            data (pandas.DataFrame): 原始数据
            
        Returns:
            pandas.DataFrame: 预处理后的数据
        """
        if data is None or data.empty:
            self.logger.warning("没有数据需要预处理")
            return data
        
        self.logger.debug(f"对数据进行预处理，原始数据形状: {data.shape}")
        # 子类可以重写此方法进行更复杂的预处理
        return data 