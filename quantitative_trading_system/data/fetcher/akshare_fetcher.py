#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于AKShare的数据抓取器
"""
import time
import pandas as pd
from datetime import datetime, timedelta

try:
    import akshare as ak
except ImportError:
    raise ImportError("请先安装akshare包: pip install akshare")

from quantitative_trading_system.data.fetcher.base_fetcher import BaseFetcher
from quantitative_trading_system.config.config import DATA_SOURCE_CONFIG


class AKShareFetcher(BaseFetcher):
    """基于AKShare的数据抓取器"""
    
    def __init__(self):
        """初始化AKShare数据抓取器"""
        super().__init__(data_source="akshare")
        self.config = DATA_SOURCE_CONFIG.get('sources', {}).get('akshare', {})
        self.rate_limit = self.config.get('rate_limit', 200)
        self.logger.info(f"初始化AKShare数据抓取器，请求频率限制: {self.rate_limit}次/分钟")
    
    def fetch_data(self, symbols, start_date=None, end_date=None, freq='daily'):
        """
        从AKShare获取股票数据
        
        Args:
            symbols (list): 股票代码列表
            start_date (str, optional): 开始日期，格式YYYY-MM-DD. Defaults to None.
            end_date (str, optional): 结束日期，格式YYYY-MM-DD. Defaults to None.
            freq (str, optional): 数据频率，daily, weekly, monthly或分钟频率. Defaults to 'daily'.
            
        Returns:
            pandas.DataFrame: 抓取的股票数据
        """
        # 验证参数
        if not self.validate_params(symbols, start_date, end_date, freq):
            return None
        
        # 设置默认的结束日期为今天
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 设置默认的开始日期为一年前
        if not start_date:
            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
        
        self.logger.info(f"开始获取股票数据: symbols={symbols}, start_date={start_date}, end_date={end_date}, freq={freq}")
        
        result_df = pd.DataFrame()
        
        for i, symbol in enumerate(symbols):
            self.logger.info(f"正在获取股票 {symbol} 的{freq}数据，进度: {i+1}/{len(symbols)}")
            
            try:
                # 根据频率选择不同的API
                if freq == 'daily':
                    self.logger.debug(f"调用日线数据获取函数: symbol={symbol}")
                    df = self._fetch_daily_data(symbol, start_date, end_date)
                elif freq == 'weekly':
                    self.logger.debug(f"调用周线数据获取函数: symbol={symbol}")
                    df = self._fetch_weekly_data(symbol, start_date, end_date)
                elif freq == 'monthly':
                    self.logger.debug(f"调用月线数据获取函数: symbol={symbol}")
                    df = self._fetch_monthly_data(symbol, start_date, end_date)
                elif freq in ['1min', '5min', '15min', '30min', '60min']:
                    self.logger.debug(f"调用分钟线数据获取函数: symbol={symbol}, freq={freq}")
                    df = self._fetch_minute_data(symbol, start_date, end_date, freq)
                else:
                    self.logger.error(f"不支持的数据频率: {freq}")
                    continue
                
                if df is not None and not df.empty:
                    # 添加股票代码列
                    df['symbol'] = symbol
                    result_df = pd.concat([result_df, df], ignore_index=True)
                    self.logger.info(f"股票 {symbol} 数据获取成功，记录数: {len(df)}")
                else:
                    self.logger.warning(f"获取股票 {symbol} 的{freq}数据为空")
                    # 尝试不同的股票代码格式
                    alt_formats = []
                    if not symbol.startswith(('sh', 'sz')) and not symbol.endswith(('.SH', '.SZ')):
                        if symbol.startswith(('0', '2', '3')):
                            alt_formats.append(f"sz{symbol}")
                        elif symbol.startswith(('6', '9')):
                            alt_formats.append(f"sh{symbol}")
                    
                    if alt_formats:
                        self.logger.info(f"尝试使用替代格式: {alt_formats}")
                        for alt_format in alt_formats:
                            try:
                                self.logger.debug(f"尝试替代格式: {alt_format}")
                                if freq == 'daily':
                                    alt_df = self._fetch_daily_data(alt_format, start_date, end_date)
                                elif freq == 'weekly':
                                    alt_df = self._fetch_weekly_data(alt_format, start_date, end_date)
                                elif freq == 'monthly':
                                    alt_df = self._fetch_monthly_data(alt_format, start_date, end_date)
                                elif freq in ['1min', '5min', '15min', '30min', '60min']:
                                    alt_df = self._fetch_minute_data(alt_format, start_date, end_date, freq)
                                else:
                                    continue
                                
                                if alt_df is not None and not alt_df.empty:
                                    self.logger.info(f"使用替代格式 {alt_format} 成功获取到数据，记录数: {len(alt_df)}")
                                    # 添加原始股票代码列
                                    alt_df['symbol'] = symbol
                                    result_df = pd.concat([result_df, alt_df], ignore_index=True)
                                    break
                                else:
                                    self.logger.warning(f"使用替代格式 {alt_format} 获取的数据仍为空")
                            except Exception as e:
                                self.logger.error(f"尝试替代格式 {alt_format} 出错: {str(e)}")
                
                # 频率限制
                time.sleep(60 / self.rate_limit)
                
            except Exception as e:
                self.logger.error(f"获取股票 {symbol} 数据时出错: {str(e)}")
                import traceback
                self.logger.error(f"详细错误信息: {traceback.format_exc()}")
        
        # 汇总结果
        if not result_df.empty:
            self.logger.info(f"全部数据获取完成，总记录数: {len(result_df)}, 股票数: {result_df['symbol'].nunique()}")
            # 按股票分组统计
            for symbol, group in result_df.groupby('symbol'):
                self.logger.info(f"股票 {symbol} 获取的记录数: {len(group)}")
        else:
            self.logger.warning(f"所有股票的数据获取均为空! symbols={symbols}, start_date={start_date}, end_date={end_date}, freq={freq}")
            self.logger.warning("请检查：1. 股票代码格式是否正确; 2. 日期范围是否有效; 3. 是否使用了正确的数据频率")
        
        return self.preprocess_data(result_df)
    
    def _fetch_daily_data(self, symbol, start_date, end_date):
        """获取日线数据"""
        try:
            # 转换日期格式，从YYYY-MM-DD到YYYYMMDD
            start_date_fmt = start_date.replace('-', '')
            end_date_fmt = end_date.replace('-', '')
            
            # 判断股票市场
            if symbol.endswith('.SH') or symbol.endswith('.SZ'):
                # 如果已经有后缀，提取股票代码部分
                formatted_symbol = symbol.split('.')[0]
            elif symbol.startswith(('6', '9')):
                formatted_symbol = symbol  # 上海市场
            elif symbol.startswith(('0', '2', '3')):
                formatted_symbol = symbol  # 深圳市场
            else:
                formatted_symbol = symbol  # 保持原样
            
            # 获取A股历史数据 - 根据测试结果，不使用后缀
            df = ak.stock_zh_a_hist(symbol=formatted_symbol, period="daily", 
                                   start_date=start_date_fmt, end_date=end_date_fmt, 
                                   adjust="qfq")
            
            # 检查返回的数据
            if df.empty:
                self.logger.warning(f"获取股票 {symbol} 日线数据为空")
                return None
            
            # 重命名列以统一格式
            df.rename(columns={
                '日期': 'date',
                '股票代码': 'code',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '换手率': 'turnover'
            }, inplace=True)
            
            # 确保日期列格式一致
            df['date'] = pd.to_datetime(df['date'])
            
            return df
        
        except Exception as e:
            self.logger.error(f"获取股票 {symbol} 日线数据出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _fetch_weekly_data(self, symbol, start_date, end_date):
        """获取周线数据"""
        try:
            # 转换日期格式，从YYYY-MM-DD到YYYYMMDD
            start_date_fmt = start_date.replace('-', '')
            end_date_fmt = end_date.replace('-', '')
            
            if symbol.endswith('.SH') or symbol.endswith('.SZ'):
                # 如果已经有后缀，提取股票代码部分
                formatted_symbol = symbol.split('.')[0]
            elif symbol.startswith(('6', '9')):
                formatted_symbol = symbol  # 上海市场
            elif symbol.startswith(('0', '2', '3')):
                formatted_symbol = symbol  # 深圳市场
            else:
                formatted_symbol = symbol
            
            df = ak.stock_zh_a_hist(symbol=formatted_symbol, period="weekly", 
                                   start_date=start_date_fmt, end_date=end_date_fmt, 
                                   adjust="qfq")
            
            # 检查返回的数据
            if df.empty:
                self.logger.warning(f"获取股票 {symbol} 周线数据为空")
                return None
            
            df.rename(columns={
                '日期': 'date',
                '股票代码': 'code',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '换手率': 'turnover'
            }, inplace=True)
            
            df['date'] = pd.to_datetime(df['date'])
            
            return df
        
        except Exception as e:
            self.logger.error(f"获取股票 {symbol} 周线数据出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _fetch_monthly_data(self, symbol, start_date, end_date):
        """获取月线数据"""
        try:
            # 转换日期格式，从YYYY-MM-DD到YYYYMMDD
            start_date_fmt = start_date.replace('-', '')
            end_date_fmt = end_date.replace('-', '')
            
            if symbol.endswith('.SH') or symbol.endswith('.SZ'):
                # 如果已经有后缀，提取股票代码部分
                formatted_symbol = symbol.split('.')[0]
            elif symbol.startswith(('6', '9')):
                formatted_symbol = symbol  # 上海市场
            elif symbol.startswith(('0', '2', '3')):
                formatted_symbol = symbol  # 深圳市场
            else:
                formatted_symbol = symbol
            
            df = ak.stock_zh_a_hist(symbol=formatted_symbol, period="monthly", 
                                   start_date=start_date_fmt, end_date=end_date_fmt, 
                                   adjust="qfq")
            
            # 检查返回的数据
            if df.empty:
                self.logger.warning(f"获取股票 {symbol} 月线数据为空")
                return None
                
            df.rename(columns={
                '日期': 'date',
                '股票代码': 'code',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '换手率': 'turnover'
            }, inplace=True)
            
            df['date'] = pd.to_datetime(df['date'])
            
            return df
        
        except Exception as e:
            self.logger.error(f"获取股票 {symbol} 月线数据出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _fetch_minute_data(self, symbol, start_date, end_date, freq):
        """获取分钟线数据"""
        try:
            # 转换日期格式，从YYYY-MM-DD到YYYYMMDD
            start_date_fmt = start_date.replace('-', '')
            end_date_fmt = end_date.replace('-', '')
            
            # 转换频率格式
            freq_map = {
                '1min': '1', 
                '5min': '5', 
                '15min': '15',
                '30min': '30',
                '60min': '60'
            }
            ak_freq = freq_map.get(freq)
            
            if not ak_freq:
                self.logger.error(f"不支持的分钟频率: {freq}")
                return None
            
            if symbol.endswith('.SH') or symbol.endswith('.SZ'):
                # 如果已经有后缀，提取股票代码部分
                formatted_symbol = symbol.split('.')[0]
            elif symbol.startswith(('6', '9')):
                formatted_symbol = symbol  # 上海市场
            elif symbol.startswith(('0', '2', '3')):
                formatted_symbol = symbol  # 深圳市场
            else:
                formatted_symbol = symbol
            
            # 获取分钟级别数据
            try:
                df = ak.stock_zh_a_hist_min_em(symbol=formatted_symbol, period=ak_freq, 
                                            start_date=start_date_fmt, end_date=end_date_fmt,
                                            adjust="qfq")
            except Exception as e:
                self.logger.error(f"使用stock_zh_a_hist_min_em获取分钟数据失败: {str(e)}")
                # 尝试使用另一个API
                try:
                    df = ak.stock_zh_a_minute(symbol=formatted_symbol, period=ak_freq,
                                          adjust="qfq")
                except Exception as e2:
                    self.logger.error(f"使用stock_zh_a_minute获取分钟数据也失败: {str(e2)}")
                    return None
            
            # 检查返回的数据
            if df.empty:
                self.logger.warning(f"获取股票 {symbol} {freq}数据为空")
                return None
            
            # 重命名列以统一格式 - 根据返回的实际列名调整
            column_mappings = {
                '时间': 'datetime',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '最新价': 'last',
            }
            
            # 仅重命名存在的列
            rename_cols = {}
            for old_col, new_col in column_mappings.items():
                if old_col in df.columns:
                    rename_cols[old_col] = new_col
            
            if rename_cols:
                df.rename(columns=rename_cols, inplace=True)
            
            # 确保有datetime列
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['date'] = df['datetime'].dt.date
            else:
                self.logger.warning(f"分钟数据中没有datetime列，将创建一个")
                if '日期' in df.columns and '时间' in df.columns:
                    df['datetime'] = pd.to_datetime(df['日期'] + ' ' + df['时间'])
                    df['date'] = df['datetime'].dt.date
            
            # 添加股票代码列
            df['symbol'] = symbol
            
            return df
        
        except Exception as e:
            self.logger.error(f"获取股票 {symbol} {freq}数据出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def preprocess_data(self, data):
        """
        对AKShare数据进行预处理
        
        Args:
            data (pandas.DataFrame): 原始数据
            
        Returns:
            pandas.DataFrame: 预处理后的数据
        """
        if data is None or data.empty:
            return data
        
        try:
            # 调用父类的预处理方法
            data = super().preprocess_data(data)
            
            # AKShare特有的预处理逻辑
            # 1. 排序
            if 'date' in data.columns:
                data.sort_values(['symbol', 'date'], inplace=True)
            elif 'datetime' in data.columns:
                data.sort_values(['symbol', 'datetime'], inplace=True)
            
            # 2. 处理缺失值 - 使用新的方法代替被弃用的方法
            data = data.ffill()
            
            # 3. 计算其他可能需要的指标 - 添加更多的数据验证
            required_columns = ['close', 'open', 'high', 'low', 'symbol']
            if all(col in data.columns for col in required_columns) and len(data) > 1:
                # 计算涨跌幅(如果原始数据中没有)
                if 'change_pct' not in data.columns:
                    try:
                        data['change_pct'] = data.groupby('symbol')['close'].pct_change() * 100
                    except Exception as e:
                        self.logger.warning(f"计算涨跌幅失败: {str(e)}")
                
                # 计算真实波动幅度TR - 使用更安全的方法
                try:
                    # 首先按符号分组处理，避免不同股票之间的计算
                    data['tr'] = data['high'] - data['low']  # 默认值是高低差
                    
                    # 对每个股票单独计算TR
                    for symbol, group in data.groupby('symbol'):
                        if len(group) <= 1:
                            continue
                            
                        # 计算前一日收盘价与当日最高价的差的绝对值
                        high_close_diff = (group['high'] - group['close'].shift(1)).abs()
                        
                        # 计算前一日收盘价与当日最低价的差的绝对值
                        low_close_diff = (group['low'] - group['close'].shift(1)).abs()
                        
                        # 计算真实波动幅度
                        group_tr = pd.DataFrame({
                            'hl_diff': group['high'] - group['low'],
                            'hc_diff': high_close_diff,
                            'lc_diff': low_close_diff
                        }).max(axis=1)
                        
                        # 更新原始数据框中的TR值
                        data.loc[group.index, 'tr'] = group_tr.values
                        
                except Exception as e:
                    self.logger.warning(f"计算TR失败: {str(e)}")
                    # 如果计算失败，简单地使用高低差
                    data['tr'] = data['high'] - data['low']
            
            return data
            
        except Exception as e:
            self.logger.error(f"数据预处理失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            # 返回原始数据，确保不会因处理失败而丢失数据
            return data 