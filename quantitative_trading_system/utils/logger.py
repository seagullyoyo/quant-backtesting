#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
"""
import os
import logging
import logging.handlers
from datetime import datetime
import inspect
import traceback

from quantitative_trading_system.config.config import LOG_CONFIG


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name) 


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加调用堆栈信息
        error_stack = traceback.format_stack()[:-2]
        error_stack_str = ''.join(error_stack)
        self.logger.error(f"{error_msg}\n调用堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        # 添加完整的堆栈跟踪
        error_stack = traceback.format_stack()
        error_stack_str = ''.join(error_stack)
        self.logger.critical(f"{error_msg}\n完整堆栈:\n{error_stack_str}", *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)
        self.logger.exception(error_msg, *args, **kwargs)


def get_logger(name):
    """
    获取指定名称的增强日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        EnhancedLogger: 增强的日志记录器实例
    """
    return EnhancedLogger(name)


def setup_logger(log_level=None, log_file=None):
    """
    设置日志系统
    
    Args:
        log_level (str, optional): 日志级别. Defaults to None.
        log_file (str, optional): 日志文件路径. Defaults to None.
    """
    # 获取配置的日志级别或使用传入的参数
    level = log_level or LOG_CONFIG.get('log_level', 'INFO')
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # 创建日志目录
    log_dir = LOG_CONFIG.get('log_dir', './logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 如果没有指定日志文件，生成一个带时间戳的日志文件
    if not log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'quant_trading_{timestamp}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 移除已存在的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    # 增强的控制台格式
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG.get('max_log_file_size', 10*1024*1024),
        backupCount=LOG_CONFIG.get('backup_count', 5)
    )
    file_handler.setLevel(numeric_level)
    # 增强的文件格式，包含更多上下文信息
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(pathname)s:%(lineno)d) - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置一些第三方库的日志级别为WARNING，减少噪音
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    return root_logger


class EnhancedLogger:
    """增强的日志记录器，提供更多的上下文信息"""
    
    def __init__(self, name):
        """初始化增强日志记录器"""
        self.logger = logging.getLogger(name)
    
    def _add_context(self, msg):
        """添加上下文信息到日志消息"""
        frame = inspect.currentframe().f_back.f_back
        func_name = frame.f_code.co_name
        return f"[{func_name}] {msg}"
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._add_context(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(self._add_context(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._add_context(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        error_msg = self._add_context(msg)