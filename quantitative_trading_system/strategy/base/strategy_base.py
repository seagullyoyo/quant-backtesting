#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略基类模块
定义量化交易策略的标准接口
"""
import abc
import pandas as pd
from datetime import datetime

from quantitative_trading_system.utils.logger import get_logger


class StrategyBase(abc.ABC):
    """量化交易策略基类"""
    
    def __init__(self, name=None, author=None, description=None):
        """
        初始化策略
        
        Args:
            name (str, optional): 策略名称. Defaults to None.
            author (str, optional): 策略作者. Defaults to None.
            description (str, optional): 策略描述. Defaults to None.
        """
        self.logger = get_logger(self.__class__.__name__)
        
        # 策略元数据
        self.name = name or self.__class__.__name__
        self.author = author
        self.description = description
        self.creation_time = datetime.now()
        
        # 策略状态
        self.is_initialized = False
        self.is_running = False
        self.current_date = None
        self.current_datetime = None
        
        # 策略参数
        self.parameters = {}
        
        # 策略结果
        self.positions = {}
        self.signals = {}
        self.portfolio_value = 0
        
        self.logger.info(f"创建策略: {self.name}")
    
    def set_parameters(self, **kwargs):
        """
        设置策略参数
        
        Args:
            **kwargs: 策略参数
        """
        for key, value in kwargs.items():
            self.parameters[key] = value
        
        self.logger.info(f"设置策略参数: {kwargs}")
    
    @abc.abstractmethod
    def initialize(self, context):
        """
        初始化策略，在策略回测/执行开始前调用
        
        Args:
            context: 策略上下文对象
        """
        pass
    
    @abc.abstractmethod
    def handle_data(self, context, data):
        """
        处理每个时间点的数据，生成交易信号
        
        Args:
            context: 策略上下文对象
            data: 当前时间点的市场数据
        """
        pass
    
    def before_trading_start(self, context, data):
        """
        每个交易日开始前调用
        
        Args:
            context: 策略上下文对象
            data: 当前交易日的市场数据
        """
        pass
    
    def after_trading_end(self, context, data):
        """
        每个交易日结束后调用
        
        Args:
            context: 策略上下文对象
            data: 当前交易日的市场数据
        """
        pass
    
    def on_strategy_start(self, context):
        """
        策略启动时调用
        
        Args:
            context: 策略上下文对象
        """
        self.is_running = True
        self.logger.info(f"策略 {self.name} 启动")
    
    def on_strategy_stop(self, context):
        """
        策略停止时调用
        
        Args:
            context: 策略上下文对象
        """
        self.is_running = False
        self.logger.info(f"策略 {self.name} 停止")
    
    def on_order_creation(self, context, order):
        """
        创建订单时调用
        
        Args:
            context: 策略上下文对象
            order: 订单对象
        """
        pass
    
    def on_order_filled(self, context, order):
        """
        订单成交时调用
        
        Args:
            context: 策略上下文对象
            order: 订单对象
        """
        pass
    
    def on_order_canceled(self, context, order):
        """
        订单取消时调用
        
        Args:
            context: 策略上下文对象
            order: 订单对象
        """
        pass
    
    def on_order_rejected(self, context, order):
        """
        订单被拒绝时调用
        
        Args:
            context: 策略上下文对象
            order: 订单对象
        """
        pass
    
    def generate_signals(self, context, data):
        """
        生成交易信号的通用方法
        
        Args:
            context: 策略上下文对象
            data: 当前时间点的市场数据
            
        Returns:
            dict: 交易信号字典
        """
        # 调用子类实现的handle_data方法
        self.handle_data(context, data)
        return self.signals
    
    def get_portfolio_value(self):
        """
        获取当前组合价值
        
        Returns:
            float: 组合价值
        """
        return self.portfolio_value
    
    def get_positions(self):
        """
        获取当前持仓
        
        Returns:
            dict: 持仓字典
        """
        return self.positions
    
    def get_signals(self):
        """
        获取当前交易信号
        
        Returns:
            dict: 交易信号字典
        """
        return self.signals
    
    def save(self, path):
        """
        保存策略配置
        
        Args:
            path (str): 保存路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            import json
            
            # 构建策略配置字典
            config = {
                'name': self.name,
                'author': self.author,
                'description': self.description,
                'creation_time': self.creation_time.strftime('%Y-%m-%d %H:%M:%S'),
                'parameters': self.parameters,
                'class_name': self.__class__.__name__,
                'module_name': self.__class__.__module__
            }
            
            # 保存为JSON文件
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"策略配置已保存到: {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存策略配置失败: {str(e)}")
            return False
    
    @classmethod
    def load(cls, path):
        """
        加载策略配置
        
        Args:
            path (str): 配置文件路径
            
        Returns:
            StrategyBase: 策略实例
        """
        try:
            import json
            import importlib
            
            # 加载JSON配置
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 导入策略类
            module_name = config.get('module_name')
            class_name = config.get('class_name')
            
            if not module_name or not class_name:
                raise ValueError("配置文件缺少module_name或class_name字段")
            
            module = importlib.import_module(module_name)
            strategy_class = getattr(module, class_name)
            
            # 创建策略实例
            strategy = strategy_class(
                name=config.get('name'),
                author=config.get('author'),
                description=config.get('description')
            )
            
            # 设置参数
            strategy.set_parameters(**config.get('parameters', {}))
            
            logger = get_logger(cls.__name__)
            logger.info(f"从配置加载策略: {path}")
            return strategy
            
        except Exception as e:
            logger = get_logger(cls.__name__)
            logger.error(f"加载策略配置失败: {str(e)}")
            return None 