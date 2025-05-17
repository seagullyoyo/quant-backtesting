#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据API模块
提供统一的数据访问接口
"""
import pandas as pd
from functools import lru_cache
from datetime import datetime, timedelta

from quantitative_trading_system.utils.logger import get_logger
from quantitative_trading_system.data.fetcher.akshare_fetcher import AKShareFetcher
from quantitative_trading_system.data.storage.csv_storage import CSVStorage
from quantitative_trading_system.config.config import API_CONFIG


class DataAPI:
    """数据API类，提供统一的数据访问接口"""
    
    def __init__(self):
        """初始化数据API"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("初始化数据API")
        
        # 初始化数据抓取器
        self.fetcher = AKShareFetcher()
        
        # 初始化数据存储器
        self.storage = CSVStorage()
        
        # 配置
        self.config = API_CONFIG.get('data_api', {})
        self.cache_time = self.config.get('cache_time', 300)  # 缓存时间，单位：秒
    
    @lru_cache(maxsize=128)
    def get_price(self, symbols, start_date=None, end_date=None, freq='daily', fields=None, 
                adjust=True, skip_paused=True, use_cache=True):
        """
        获取股票价格数据
        
        Args:
            symbols (str or list): 股票代码或代码列表
            start_date (str, optional): 开始日期，格式YYYY-MM-DD. Defaults to None.
            end_date (str, optional): 结束日期，格式YYYY-MM-DD. Defaults to None.
            freq (str, optional): 数据频率，daily/weekly/monthly或分钟频率. Defaults to 'daily'.
            fields (list, optional): 需要的字段列表. Defaults to None.
            adjust (bool, optional): 是否使用复权数据. Defaults to True.
            skip_paused (bool, optional): 是否跳过停牌日期. Defaults to True.
            use_cache (bool, optional): 是否使用缓存数据. Defaults to True.
            
        Returns:
            pandas.DataFrame: 股票价格数据
        """
        # 始终启用缓存，忽略use_cache参数
        use_cache = True
        
        # 转换单个股票代码为列表
        if isinstance(symbols, str):
            symbols = [symbols]
            
        # 标准化股票代码格式
        normalized_symbols = []
        for symbol in symbols:
            norm_symbol = self._normalize_stock_code(symbol)
            normalized_symbols.append(norm_symbol)
            if norm_symbol != symbol:
                self.logger.info(f"股票代码已标准化: {symbol} -> {norm_symbol}")
        
        symbols = normalized_symbols
        
        # 设置默认的结束日期为今天
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 设置默认的开始日期为一年前
        if not start_date:
            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
        
        self.logger.info(f"请求数据: symbols={symbols}, start_date={start_date}, end_date={end_date}, freq={freq}, use_cache={use_cache}")
        
        # 尝试从存储中加载数据
        result_df = pd.DataFrame()
        need_fetch_symbols = []
        
        if use_cache:
            for symbol in symbols:
                try:
                    # 从存储中加载数据
                    conditions = {}
                    if start_date:
                        if freq.endswith('min'):
                            conditions['datetime'] = f">= '{start_date}'"
                        else:
                            conditions['date'] = f">= '{start_date}'"
                    if end_date:
                        if freq.endswith('min'):
                            conditions['datetime'] = f"<= '{end_date}'"
                        else:
                            conditions['date'] = f"<= '{end_date}'"
                    
                    self.logger.debug(f"尝试从缓存加载数据: symbol={symbol}, conditions={conditions}")
                    
                    df = self.storage.load(
                        collection=freq, 
                        conditions=conditions, 
                        symbol=symbol,
                        freq=freq
                    )
                    
                    if not df.empty:
                        # 检查数据是否最新
                        if freq.endswith('min'):
                            latest_date = df['datetime'].max()
                        else:
                            latest_date = df['date'].max()
                        
                        latest_date_str = pd.to_datetime(latest_date).strftime('%Y-%m-%d')
                        current_date_str = datetime.now().strftime('%Y-%m-%d')
                        
                        self.logger.debug(f"从缓存加载的数据: symbol={symbol}, 记录数={len(df)}, 最新日期={latest_date_str}")
                        
                        # 如果数据不是今天的，且今天是交易日，则需要重新获取
                        if latest_date_str < current_date_str:
                            # 判断最后更新时间是否超过缓存时间
                            cache_expired = True
                            # TODO: 添加交易日判断逻辑
                        else:
                            cache_expired = False
                        
                        if not cache_expired:
                            self.logger.info(f"使用缓存数据: symbol={symbol}, 记录数={len(df)}, 日期范围={df['date'].min()} 至 {df['date'].max()}")
                            result_df = pd.concat([result_df, df])
                            continue
                    else:
                        self.logger.info(f"缓存中未找到数据: symbol={symbol}, freq={freq}")
                
                except Exception as e:
                    self.logger.error(f"从存储加载数据失败: symbol={symbol}, error={str(e)}")
                
                # 如果走到这里，说明需要重新获取数据
                need_fetch_symbols.append(symbol)
        else:
            need_fetch_symbols = symbols
        
        # 如果有需要重新获取的数据
        if need_fetch_symbols:
            try:
                self.logger.info(f"从数据源获取数据: symbols={need_fetch_symbols}, start_date={start_date}, end_date={end_date}, freq={freq}")
                fetched_df = self.fetcher.fetch_data(
                    symbols=need_fetch_symbols, 
                    start_date=start_date, 
                    end_date=end_date, 
                    freq=freq
                )
                
                if not fetched_df.empty:
                    self.logger.info(f"成功获取数据，记录总数: {len(fetched_df)}")
                    
                    # 保存到存储
                    for symbol in need_fetch_symbols:
                        symbol_df = fetched_df[fetched_df['symbol'] == symbol]
                        if not symbol_df.empty:
                            self.logger.info(f"保存数据到存储: symbol={symbol}, 记录数={len(symbol_df)}")
                            self.storage.save(
                                data=symbol_df, 
                                collection=freq, 
                                symbol=symbol, 
                                freq=freq
                            )
                        else:
                            self.logger.warning(f"获取的数据中没有股票 {symbol} 的记录，请检查股票代码格式是否正确")
                    
                    # 合并结果
                    result_df = pd.concat([result_df, fetched_df])
                else:
                    symbol_list = ", ".join(need_fetch_symbols)
                    self.logger.warning(f"从数据源获取数据为空。请求参数: symbols=[{symbol_list}], start_date={start_date}, end_date={end_date}, freq={freq}")
            
            except Exception as e:
                self.logger.error(f"获取数据失败: symbols={need_fetch_symbols}, error={str(e)}")
        
        # 数据后处理
        if not result_df.empty:
            # 记录获取的数据信息
            grouped = result_df.groupby('symbol').size()
            for symbol, count in grouped.items():
                self.logger.info(f"返回数据: symbol={symbol}, 记录数={count}")
            
            # 排序
            if freq.endswith('min'):
                result_df.sort_values(['symbol', 'datetime'], inplace=True)
            else:
                result_df.sort_values(['symbol', 'date'], inplace=True)
            
            # 处理字段
            if fields:
                # 确保symbol字段始终在结果中
                if 'symbol' not in fields:
                    fields.append('symbol')
                
                # 确保日期字段始终在结果中
                if freq.endswith('min') and 'datetime' not in fields:
                    fields.append('datetime')
                elif not freq.endswith('min') and 'date' not in fields:
                    fields.append('date')
                
                # 过滤字段
                available_fields = [field for field in fields if field in result_df.columns]
                result_df = result_df[available_fields]
            
            # 处理停牌
            if skip_paused:
                # 简单地通过成交量为0来判断停牌
                if 'volume' in result_df.columns:
                    before_count = len(result_df)
                    result_df = result_df[result_df['volume'] > 0]
                    after_count = len(result_df)
                    
                    if before_count > after_count:
                        self.logger.info(f"过滤停牌记录: 过滤前={before_count}, 过滤后={after_count}, 过滤掉={before_count-after_count}")
        else:
            symbol_list = ", ".join(symbols)
            self.logger.warning(f"最终获取的数据为空！请求参数: symbols=[{symbol_list}], start_date={start_date}, end_date={end_date}, freq={freq}")
        
        return result_df
    
    def get_fundamental(self, symbols, fields=None, start_date=None, end_date=None, use_cache=True):
        """
        获取股票基本面数据
        
        Args:
            symbols (str or list): 股票代码或代码列表
            fields (list, optional): 需要的字段列表. Defaults to None.
            start_date (str, optional): 开始日期，格式YYYY-MM-DD. Defaults to None.
            end_date (str, optional): 结束日期，格式YYYY-MM-DD. Defaults to None.
            use_cache (bool, optional): 是否使用缓存数据. Defaults to True.
            
        Returns:
            pandas.DataFrame: 股票基本面数据
        """
        self.logger.info("获取股票基本面数据")
        # TODO: 实现基本面数据获取逻辑
        # 这里暂时返回空DataFrame，后续完善
        return pd.DataFrame()
    
    def get_industry(self, symbols, standard='sw'):
        """
        获取股票所属行业
        
        Args:
            symbols (str or list): 股票代码或代码列表
            standard (str, optional): 行业分类标准. Defaults to 'sw'.
            
        Returns:
            pandas.DataFrame: 股票行业数据
        """
        self.logger.info("获取股票行业数据")
        # TODO: 实现行业数据获取逻辑
        # 这里暂时返回空DataFrame，后续完善
        return pd.DataFrame()
    
    def get_index_stocks(self, index_symbol, date=None):
        """
        获取指数成分股
        
        Args:
            index_symbol (str): 指数代码
            date (str, optional): 查询日期，格式YYYY-MM-DD. Defaults to None.
            
        Returns:
            list: 成分股列表
        """
        self.logger.info(f"获取指数 {index_symbol} 成分股")
        # TODO: 实现指数成分股获取逻辑
        # 这里暂时返回空列表，后续完善
        return []
    
    def get_index_weights(self, index_symbol, date=None):
        """
        获取指数成分股权重
        
        Args:
            index_symbol (str): 指数代码
            date (str, optional): 查询日期，格式YYYY-MM-DD. Defaults to None.
            
        Returns:
            pandas.DataFrame: 成分股权重数据
        """
        self.logger.info(f"获取指数 {index_symbol} 成分股权重")
        # TODO: 实现指数成分股权重获取逻辑
        # 这里暂时返回空DataFrame，后续完善
        return pd.DataFrame()
    
    def get_trading_dates(self, start_date=None, end_date=None):
        """
        获取交易日历
        
        Args:
            start_date (str, optional): 开始日期. Defaults to None.
            end_date (str, optional): 结束日期. Defaults to None.
            
        Returns:
            list: 交易日列表
        """
        self.logger.info("获取交易日历")
        # TODO: 实现交易日历获取逻辑
        # 这里暂时返回空列表，后续完善
        return []
    
    def clear_cache(self):
        """清除缓存"""
        self.get_price.cache_clear()
        self.logger.info("已清除DataAPI缓存")
        
    def _normalize_stock_code(self, code):
        """
        标准化股票代码格式，确保缓存一致性
        
        Args:
            code (str): 原始股票代码
        
        Returns:
            str: 标准化后的股票代码
        """
        # 如果为空或非字符串，直接返回
        if not code or not isinstance(code, str):
            return code
            
        # 去除前缀和后缀，只保留数字部分
        if code.startswith('sh') or code.startswith('sz'):
            code = code[2:]
        elif code.endswith('.SH') or code.endswith('.SZ'):
            code = code.split('.')[0]
        
        # 为股票代码添加标准后缀
        if code.startswith(('0', '2', '3')):
            return code + '.SZ'
        elif code.startswith(('6', '9')):
            return code + '.SH'
        elif code.startswith('000'):  # 指数代码特殊处理
            return code + '.SH' if code in ['000001', '000300'] else code + '.SZ'
        
        return code


# 创建全局单例实例
data_api = DataAPI() 