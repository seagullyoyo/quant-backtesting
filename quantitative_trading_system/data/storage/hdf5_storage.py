#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HDF5数据存储模块
用于存储历史行情数据
"""
import os
import pandas as pd
from datetime import datetime

from quantitative_trading_system.data.storage.base_storage import BaseStorage
from quantitative_trading_system.config.config import DATABASE_CONFIG


class HDF5Storage(BaseStorage):
    """HDF5数据存储类，用于存储历史行情数据"""
    
    def __init__(self):
        """初始化HDF5存储器"""
        super().__init__(storage_type="hdf5")
        self.config = DATABASE_CONFIG.get('history_data', {})
        self.base_path = self.config.get('path', './data/storage/history_data')
        
        # 创建存储目录
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            self.logger.info(f"创建HDF5存储目录: {self.base_path}")
    
    def _get_file_path(self, collection, **kwargs):
        """
        获取HDF5文件路径
        
        Args:
            collection (str): 数据集名称，如'daily', 'minute'
            **kwargs: 其他参数，如symbol, freq等
        
        Returns:
            str: HDF5文件路径
        """
        # 创建对应的子目录
        sub_dir = os.path.join(self.base_path, collection)
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
        
        # 如果指定了股票代码，则使用股票代码作为文件名
        symbol = kwargs.get('symbol')
        freq = kwargs.get('freq', 'daily')
        
        if symbol:
            # 为单一股票创建文件
            filename = f"{symbol}_{freq}.h5"
        else:
            # 为整个市场创建文件
            # 使用当前日期作为文件名的一部分，避免频繁覆盖
            date_str = kwargs.get('date_str', datetime.now().strftime('%Y%m%d'))
            filename = f"market_{freq}_{date_str}.h5"
        
        return os.path.join(sub_dir, filename)
    
    def save(self, data, collection=None, **kwargs):
        """
        保存数据到HDF5文件
        
        Args:
            data (pandas.DataFrame): 要保存的数据
            collection (str, optional): 数据集名称，如'daily', 'minute'. Defaults to None.
            **kwargs: 其他参数，如symbol, freq, key等
            
        Returns:
            bool: 是否保存成功
        """
        if not self.validate_data(data):
            return False
        
        # 默认的集合名为daily
        collection = collection or 'daily'
        
        try:
            # 获取文件路径
            file_path = self._get_file_path(collection, **kwargs)
            
            # 获取HDF5的key
            key = kwargs.get('key', 'data')
            
            # 保存模式：append或overwrite
            mode = kwargs.get('mode', 'a')  # 默认为追加模式
            
            # 是否进行重复数据处理
            if kwargs.get('handle_duplicates', True):
                # 如果文件存在且指定了追加模式，先读取已有数据进行去重处理
                if os.path.exists(file_path) and mode == 'a':
                    existing_data = pd.DataFrame()
                    try:
                        # 确保关闭文件句柄
                        with pd.HDFStore(file_path, mode='r') as store:
                            if key in store:
                                existing_data = store[key]
                    except Exception as e:
                        self.logger.warning(f"读取现有数据失败: {str(e)}，将覆盖已有数据")
                        mode = 'w'  # 文件读取失败，直接覆盖
                    
                    if not existing_data.empty:
                        # 根据symbol和date/datetime去重
                        if 'datetime' in data.columns and 'datetime' in existing_data.columns:
                            combined_data = pd.concat([existing_data, data])
                            data = combined_data.drop_duplicates(subset=['symbol', 'datetime'], keep='last')
                        elif 'date' in data.columns and 'date' in existing_data.columns:
                            combined_data = pd.concat([existing_data, data])
                            data = combined_data.drop_duplicates(subset=['symbol', 'date'], keep='last')
                        mode = 'w'  # 切换为覆盖模式，因为已经合并了数据
            
            # 保存数据 - 使用with语句确保文件句柄被正确关闭
            with pd.HDFStore(file_path, mode=mode) as store:
                store.put(key, data, format='table', data_columns=True)
            
            self.logger.info(f"成功保存数据到HDF5文件: {file_path}, 记录数: {len(data)}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存数据到HDF5文件失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def load(self, collection=None, conditions=None, **kwargs):
        """
        从HDF5文件加载数据
        
        Args:
            collection (str, optional): 数据集名称，如'daily', 'minute'. Defaults to None.
            conditions (dict, optional): 加载条件，转换为HDF5的where条件. Defaults to None.
            **kwargs: 其他参数，如symbol, freq, key等
            
        Returns:
            pandas.DataFrame: 加载的数据
        """
        # 默认的集合名为daily
        collection = collection or 'daily'
        
        try:
            # 获取文件路径
            file_path = self._get_file_path(collection, **kwargs)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.logger.warning(f"HDF5文件不存在: {file_path}")
                return pd.DataFrame()
            
            # 获取HDF5的key
            key = kwargs.get('key', 'data')
            
            # 将conditions转换为where条件
            where = None
            if conditions:
                where_conditions = []
                for column, value in conditions.items():
                    if isinstance(value, (list, tuple)):
                        where_conditions.append(f"{column} in {value}")
                    elif value.startswith('>') or value.startswith('<') or value.startswith('='):
                        # 直接使用比较表达式
                        where_conditions.append(f"{column} {value}")
                    else:
                        # 避免使用带引号的表达式，这会导致语法错误
                        where_conditions.append(f"{column} == {value}")
                
                if where_conditions:
                    where = ' & '.join(where_conditions)
            
            # 使用with语句确保文件句柄被正确关闭
            data = pd.DataFrame()
            with pd.HDFStore(file_path, mode='r') as store:
                if key not in store:
                    self.logger.warning(f"键 {key} 在HDF5文件中不存在: {file_path}")
                    return pd.DataFrame()
                
                # 加载数据
                if where:
                    try:
                        data = store.select(key, where=where)
                    except:
                        # 如果where条件有问题，尝试不使用where条件
                        self.logger.warning(f"使用where条件查询失败，尝试加载全部数据")
                        data = store[key]
                else:
                    data = store[key]
            
            self.logger.info(f"成功从HDF5文件加载数据: {file_path}, 记录数: {len(data)}")
            return data
            
        except Exception as e:
            self.logger.error(f"从HDF5文件加载数据失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return pd.DataFrame()
    
    def delete(self, collection=None, conditions=None, **kwargs):
        """
        从HDF5文件删除数据
        
        Args:
            collection (str, optional): 数据集名称. Defaults to None.
            conditions (dict, optional): 删除条件. Defaults to None.
            **kwargs: 其他参数
            
        Returns:
            bool: 是否删除成功
        """
        # HDF5不支持直接删除部分数据，需要先加载、过滤再保存
        # 默认的集合名为daily
        collection = collection or 'daily'
        
        try:
            # 获取文件路径
            file_path = self._get_file_path(collection, **kwargs)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.logger.warning(f"HDF5文件不存在: {file_path}")
                return True  # 文件不存在视为删除成功
            
            # 如果没有条件，直接删除整个文件
            if not conditions:
                os.remove(file_path)
                self.logger.info(f"成功删除HDF5文件: {file_path}")
                return True
            
            # 加载现有数据
            key = kwargs.get('key', 'data')
            data = pd.DataFrame()
            
            # 使用with语句确保文件句柄正确关闭
            with pd.HDFStore(file_path, mode='r') as store:
                if key in store:
                    data = store[key]
                else:
                    self.logger.warning(f"键 {key} 在HDF5文件中不存在: {file_path}")
                    return True
            
            # 如果没有数据可删除
            if data.empty:
                return True
            
            # 构建过滤条件
            filter_condition = True
            for column, value in conditions.items():
                if isinstance(value, (list, tuple)):
                    filter_condition = filter_condition & (~data[column].isin(value))
                else:
                    filter_condition = filter_condition & (data[column] != value)
            
            # 过滤数据
            filtered_data = data[filter_condition]
            
            # 如果过滤后没有数据，删除文件
            if filtered_data.empty:
                os.remove(file_path)
                self.logger.info(f"过滤后无数据，删除HDF5文件: {file_path}")
                return True
            
            # 保存过滤后的数据 - 使用with语句确保文件句柄正确关闭
            with pd.HDFStore(file_path, mode='w') as store:
                store.put(key, filtered_data, format='table', data_columns=True)
            
            self.logger.info(f"成功从HDF5文件删除数据: {file_path}, 剩余记录数: {len(filtered_data)}")
            return True
            
        except Exception as e:
            self.logger.error(f"从HDF5文件删除数据失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def update(self, collection=None, conditions=None, update_data=None, **kwargs):
        """
        更新HDF5文件中的数据
        
        Args:
            collection (str, optional): 数据集名称. Defaults to None.
            conditions (dict, optional): 更新条件. Defaults to None.
            update_data (dict, optional): 更新内容. Defaults to None.
            **kwargs: 其他参数
            
        Returns:
            bool: 是否更新成功
        """
        # HDF5不支持直接更新部分数据，需要先加载、修改再保存
        if not update_data:
            self.logger.error("更新内容不能为空")
            return False
        
        # 默认的集合名为daily
        collection = collection or 'daily'
        
        try:
            # 获取文件路径
            file_path = self._get_file_path(collection, **kwargs)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.logger.warning(f"HDF5文件不存在: {file_path}")
                return False
            
            # 加载现有数据
            key = kwargs.get('key', 'data')
            data = pd.DataFrame()
            
            # 使用with语句确保文件句柄正确关闭
            with pd.HDFStore(file_path, mode='r') as store:
                if key in store:
                    data = store[key]
                else:
                    self.logger.warning(f"键 {key} 在HDF5文件中不存在: {file_path}")
                    return False
            
            # 如果没有数据可更新
            if data.empty:
                return False
            
            # 构建过滤条件
            if conditions:
                filter_condition = True
                for column, value in conditions.items():
                    if isinstance(value, (list, tuple)):
                        filter_condition = filter_condition & (data[column].isin(value))
                    else:
                        filter_condition = filter_condition & (data[column] == value)
                
                # 更新数据
                for column, value in update_data.items():
                    data.loc[filter_condition, column] = value
            else:
                # 如果没有条件，更新所有数据
                for column, value in update_data.items():
                    data[column] = value
            
            # 保存更新后的数据 - 使用with语句确保文件句柄正确关闭
            with pd.HDFStore(file_path, mode='w') as store:
                store.put(key, data, format='table', data_columns=True)
            
            self.logger.info(f"成功更新HDF5文件数据: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新HDF5文件数据失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False 