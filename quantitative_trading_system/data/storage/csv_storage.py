#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV 存储模块
提供基于 CSV 文件的数据存储功能
"""
import os
import pandas as pd
from datetime import datetime

from quantitative_trading_system.utils.logger import get_logger
from quantitative_trading_system.data.storage.base_storage import BaseStorage


class CSVStorage(BaseStorage):
    """CSV 存储类"""

    def __init__(self, data_dir=None):
        """
        初始化 CSV 存储
        
        Args:
            data_dir (str, optional): 数据存储目录. Defaults to None.
        """
        self.logger = get_logger(self.__class__.__name__)
        
        # 设置数据存储目录
        if data_dir:
            self.data_dir = data_dir
        else:
            # 默认在项目根目录下的 data 目录中
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data')
        
        # 确保目录存在
        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir)
                self.logger.info(f"创建数据目录: {self.data_dir}")
            except Exception as e:
                self.logger.error(f"创建数据目录失败: {str(e)}")
        
        self.logger.info(f"初始化 CSV 存储，数据目录: {self.data_dir}")
    
    def _get_file_path(self, collection, symbol, freq=None):
        """
        获取文件路径
        
        Args:
            collection (str): 集合名称
            symbol (str): 股票代码
            freq (str, optional): 数据频率. Defaults to None.
            
        Returns:
            str: 文件路径
        """
        # 标准化股票代码，确保相同股票使用同一缓存文件
        symbol = self._normalize_symbol(symbol)
        
        # 创建目录
        dir_path = os.path.join(self.data_dir, collection)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except Exception as e:
                self.logger.error(f"创建目录失败: {str(e)}")
                return None

        # 构造文件名
        if freq:
            file_name = f"{symbol}_{freq}.csv"
        else:
            file_name = f"{symbol}.csv"
        
        return os.path.join(dir_path, file_name)
    
    def _normalize_symbol(self, symbol):
        """
        标准化股票代码
        
        Args:
            symbol (str): 原始股票代码
            
        Returns:
            str: 标准化后的股票代码
        """
        # 如果为空或非字符串，直接返回
        if not symbol or not isinstance(symbol, str):
            return symbol
            
        # 去除前缀和后缀，只保留数字部分
        if symbol.startswith('sh') or symbol.startswith('sz'):
            symbol = symbol[2:]
        elif symbol.endswith('.SH') or symbol.endswith('.SZ'):
            symbol = symbol.split('.')[0]
        
        # 为股票代码添加标准后缀（统一格式）
        if symbol.startswith(('0', '2', '3')):
            return symbol + '.SZ'
        elif symbol.startswith(('6', '9')):
            return symbol + '.SH'
        elif symbol.startswith('000'):  # 指数代码特殊处理
            return symbol + '.SH' if symbol in ['000001', '000300'] else symbol + '.SZ'
        
        return symbol
    
    def save(self, data, collection, symbol, freq=None, mode='a'):
        """
        保存数据到 CSV 文件
        
        Args:
            data (pandas.DataFrame): 数据
            collection (str): 集合名称
            symbol (str): 股票代码
            freq (str, optional): 数据频率. Defaults to None.
            mode (str, optional): 保存模式，'w' 覆盖, 'a' 追加. Defaults to 'a'.
            
        Returns:
            bool: 是否成功
        """
        if data is None or data.empty:
            self.logger.warning("没有数据需要保存")
            return False
        
        # 获取文件路径
        file_path = self._get_file_path(collection, symbol, freq)
        if not file_path:
            return False
        
        try:
            # 如果是追加模式且文件已存在，需要处理重复数据
            if mode == 'a' and os.path.exists(file_path):
                try:
                    # 读取现有数据
                    existing_data = pd.read_csv(file_path)
                    
                    # 确定主键列
                    pk_col = 'datetime' if 'datetime' in data.columns else 'date' if 'date' in data.columns else None
                    
                    if pk_col and pk_col in existing_data.columns:
                        # 转换主键列为日期类型
                        data[pk_col] = pd.to_datetime(data[pk_col])
                        existing_data[pk_col] = pd.to_datetime(existing_data[pk_col])
                        
                        # 合并数据并删除重复项，保留最新的
                        combined_data = pd.concat([existing_data, data])
                        combined_data = combined_data.drop_duplicates(subset=[pk_col], keep='last')
                        
                        # 按日期排序
                        combined_data = combined_data.sort_values(by=pk_col)
                        
                        # 保存合并后的数据
                        combined_data.to_csv(file_path, index=False)
                        self.logger.info(f"合并数据并保存到CSV文件: {file_path}, 总条数: {len(combined_data)}")
                        return True
                except Exception as e:
                    self.logger.error(f"读取现有数据失败: {str(e)}，将覆盖已有数据")
            
            # 直接保存数据（覆盖模式或者追加模式读取现有数据失败）
            data.to_csv(file_path, index=False, mode='w')  # 使用'w'模式，确保文件被完全覆盖
            self.logger.info(f"保存数据到CSV文件: {file_path}, 条数: {len(data)}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存数据到CSV文件失败: {str(e)}")
            return False
    
    def load(self, collection, symbol=None, freq=None, conditions=None):
        """
        从 CSV 文件加载数据
        
        Args:
            collection (str): 集合名称
            symbol (str, optional): 股票代码. Defaults to None.
            freq (str, optional): 数据频率. Defaults to None.
            conditions (dict, optional): 过滤条件. Defaults to None.
            
        Returns:
            pandas.DataFrame: 数据
        """
        # 获取文件路径
        file_path = self._get_file_path(collection, symbol, freq)
        if not file_path or not os.path.exists(file_path):
            self.logger.warning(f"文件不存在: {file_path}")
            return pd.DataFrame()
        
        try:
            # 读取 CSV 文件
            df = pd.read_csv(file_path)
            
            # 转换日期列
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
            
            # 应用过滤条件
            if conditions and isinstance(conditions, dict):
                for column, condition in conditions.items():
                    if column in df.columns:
                        # 使用 eval 执行条件表达式
                        # 例如: df = df[df['date'] >= '2021-01-01']
                        try:
                            condition_str = f"df[df['{column}'] {condition}]"
                            df = eval(condition_str)
                        except Exception as e:
                            self.logger.error(f"应用条件 {column} {condition} 失败: {str(e)}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"从CSV文件加载数据失败: {str(e)}")
            return pd.DataFrame()
    
    def delete(self, collection, symbol=None, freq=None, conditions=None):
        """
        删除数据
        
        Args:
            collection (str): 集合名称
            symbol (str, optional): 股票代码. Defaults to None.
            freq (str, optional): 数据频率. Defaults to None.
            conditions (dict, optional): 过滤条件. Defaults to None.
            
        Returns:
            bool: 是否成功
        """
        # 获取文件路径
        file_path = self._get_file_path(collection, symbol, freq)
        if not file_path or not os.path.exists(file_path):
            self.logger.warning(f"文件不存在: {file_path}")
            return False
        
        try:
            # 如果有过滤条件，读取数据，应用条件后保存回去
            if conditions and isinstance(conditions, dict):
                df = self.load(collection, symbol, freq)
                if df.empty:
                    return False
                
                # 应用反向条件，保留不符合条件的数据
                filtered_df = df.copy()
                for column, condition in conditions.items():
                    if column in df.columns:
                        try:
                            # 取反条件
                            if '>=' in condition:
                                condition = condition.replace('>=', '<')
                            elif '<=' in condition:
                                condition = condition.replace('<=', '>')
                            elif '>' in condition:
                                condition = condition.replace('>', '<=')
                            elif '<' in condition:
                                condition = condition.replace('<', '>=')
                            elif '==' in condition:
                                condition = condition.replace('==', '!=')
                            elif '!=' in condition:
                                condition = condition.replace('!=', '==')
                            
                            condition_str = f"filtered_df[filtered_df['{column}'] {condition}]"
                            filtered_df = eval(condition_str)
                        except Exception as e:
                            self.logger.error(f"应用反向条件 {column} {condition} 失败: {str(e)}")
                
                # 保存过滤后的数据
                if len(filtered_df) < len(df):
                    return self.save(filtered_df, collection, symbol, freq, mode='w')
                else:
                    self.logger.warning("没有符合条件的数据被删除")
                    return False
            else:
                # 没有过滤条件，直接删除整个文件
                os.remove(file_path)
                self.logger.info(f"删除文件: {file_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def update(self, collection=None, conditions=None, update_data=None, **kwargs):
        """
        更新数据的方法
        
        Args:
            collection (str, optional): 集合名称. Defaults to None.
            conditions (dict, optional): 更新条件. Defaults to None.
            update_data (dict, optional): 更新内容. Defaults to None.
            **kwargs: 其他参数，可以包含 symbol 和 freq
            
        Returns:
            bool: 是否更新成功
        """
        if not collection or not conditions or not update_data:
            self.logger.error("更新数据需要提供集合名称、条件和更新内容")
            return False
        
        symbol = kwargs.get('symbol')
        freq = kwargs.get('freq')
        
        if not symbol:
            self.logger.error("更新数据需要提供股票代码")
            return False
        
        try:
            # 加载数据
            df = self.load(collection, symbol, freq)
            if df.empty:
                self.logger.warning(f"没有找到符合条件的数据: {collection}, {symbol}, {freq}")
                return False
            
            # 应用条件过滤
            filtered_df = df.copy()
            for column, condition in conditions.items():
                if column in df.columns:
                    try:
                        condition_str = f"filtered_df[filtered_df['{column}'] {condition}]"
                        filtered_df = eval(condition_str)
                    except Exception as e:
                        self.logger.error(f"应用条件 {column} {condition} 失败: {str(e)}")
                        return False
            
            if filtered_df.empty:
                self.logger.warning("没有符合条件的数据需要更新")
                return False
            
            # 更新数据
            for column, value in update_data.items():
                if column in filtered_df.columns:
                    filtered_df[column] = value
            
            # 更新原始数据框
            # 使用条件合并回原始数据框
            df_updated = pd.concat([df[~df.index.isin(filtered_df.index)], filtered_df])
            
            # 保存回文件
            return self.save(df_updated, collection, symbol, freq, mode='w')
            
        except Exception as e:
            self.logger.error(f"更新数据失败: {str(e)}")
            return False 