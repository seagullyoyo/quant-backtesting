#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据存储基类
"""
import abc
from quantitative_trading_system.utils.logger import get_logger


class BaseStorage(abc.ABC):
    """数据存储基类，定义数据存储的标准接口"""
    
    def __init__(self, storage_type=None):
        """
        初始化数据存储器
        
        Args:
            storage_type (str, optional): 存储类型. Defaults to None.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.storage_type = storage_type
        self.logger.info(f"初始化数据存储器: {self.__class__.__name__}, 存储类型: {storage_type}")
    
    @abc.abstractmethod
    def save(self, data, collection=None, **kwargs):
        """
        保存数据的抽象方法，子类必须实现
        
        Args:
            data: 要保存的数据
            collection (str, optional): 集合/表名. Defaults to None.
            **kwargs: 其他参数
            
        Returns:
            bool: 是否保存成功
        """
        pass
    
    @abc.abstractmethod
    def load(self, collection=None, conditions=None, **kwargs):
        """
        加载数据的抽象方法，子类必须实现
        
        Args:
            collection (str, optional): 集合/表名. Defaults to None.
            conditions (dict, optional): 查询条件. Defaults to None.
            **kwargs: 其他参数
            
        Returns:
            数据对象
        """
        pass
    
    @abc.abstractmethod
    def delete(self, collection=None, conditions=None, **kwargs):
        """
        删除数据的抽象方法，子类必须实现
        
        Args:
            collection (str, optional): 集合/表名. Defaults to None.
            conditions (dict, optional): 删除条件. Defaults to None.
            **kwargs: 其他参数
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abc.abstractmethod
    def update(self, collection=None, conditions=None, update_data=None, **kwargs):
        """
        更新数据的抽象方法，子类必须实现
        
        Args:
            collection (str, optional): 集合/表名. Defaults to None.
            conditions (dict, optional): 更新条件. Defaults to None.
            update_data (dict, optional): 更新内容. Defaults to None.
            **kwargs: 其他参数
            
        Returns:
            bool: 是否更新成功
        """
        pass
    
    def validate_data(self, data):
        """
        验证数据
        
        Args:
            data: 要验证的数据
            
        Returns:
            bool: 数据是否有效
        """
        if data is None:
            self.logger.error("数据不能为None")
            return False
        return True 