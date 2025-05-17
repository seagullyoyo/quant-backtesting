#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试不同格式的股票代码和缓存功能
"""
import os
import sys
import pandas as pd
import time
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quantitative_trading_system.utils.logger import setup_logger, get_logger
from quantitative_trading_system.data.api.data_api import DataAPI


def test_stock_codes_and_cache():
    """测试不同格式的股票代码和缓存功能"""
    # 设置日志
    setup_logger(log_level='INFO')
    logger = get_logger('test_stock_codes_cache')
    
    logger.info("开始测试不同格式的股票代码和缓存功能")
    
    # 创建数据API实例
    data_api = DataAPI()
    
    # 测试的股票代码格式
    stock_codes = [
        '000001',       # 平安银行 - 纯数字代码
        '000001.SZ',    # 平安银行 - 带后缀
        'sz000001',     # 平安银行 - 带前缀
        '600000',       # 浦发银行 - 纯数字代码
        '600000.SH',    # 浦发银行 - 带后缀
        'sh600000',     # 浦发银行 - 带前缀
    ]
    
    # 设置时间范围 - 最近30天
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    logger.info(f"测试时间范围: {start_date} 至 {end_date}")
    
    # 第一部分：测试股票代码标准化
    logger.info("\n===== 测试股票代码标准化 =====")
    for stock_code in stock_codes:
        normalized_code = data_api._normalize_stock_code(stock_code)
        logger.info(f"原始代码: {stock_code} -> 标准化后: {normalized_code}")
    
    # 第二部分：测试缓存功能
    logger.info("\n===== 测试缓存功能 =====")
    
    # 选取两个不同格式但实际相同的股票代码
    test_pairs = [
        ('000001', '000001.SZ'),  # 平安银行
        ('600000', 'sh600000')    # 浦发银行
    ]
    
    for original_code, different_format in test_pairs:
        logger.info(f"\n测试股票对: {original_code} 和 {different_format}")
        
        # 第一次调用 - 使用第一种格式，计时
        logger.info(f"第一次调用 - 使用 {original_code}")
        start_time = time.time()
        df1 = data_api.get_price(
            symbols=original_code,
            start_date=start_date,
            end_date=end_date,
            freq='daily'
        )
        time1 = time.time() - start_time
        logger.info(f"耗时: {time1:.3f}秒, 获取记录数: {len(df1)}")
        
        # 第二次调用 - 使用第一种格式，应使用缓存
        logger.info(f"第二次调用 - 再次使用 {original_code} (应使用缓存)")
        start_time = time.time()
        df2 = data_api.get_price(
            symbols=original_code,
            start_date=start_date,
            end_date=end_date,
            freq='daily'
        )
        time2 = time.time() - start_time
        logger.info(f"耗时: {time2:.3f}秒, 获取记录数: {len(df2)}")
        
        # 第三次调用 - 使用第二种格式，应使用相同缓存
        logger.info(f"第三次调用 - 使用不同格式 {different_format} (应使用相同缓存)")
        start_time = time.time()
        df3 = data_api.get_price(
            symbols=different_format,
            start_date=start_date,
            end_date=end_date,
            freq='daily'
        )
        time3 = time.time() - start_time
        logger.info(f"耗时: {time3:.3f}秒, 获取记录数: {len(df3)}")
        
        # 分析结果
        is_cached = time2 < time1 * 0.5  # 如果第二次调用时间不到第一次的一半，认为使用了缓存
        is_format_normalized = time3 < time1 * 0.5  # 如果使用不同格式也很快，说明代码标准化工作正常
        
        logger.info(f"缓存状态: {'有效' if is_cached else '无效'}")
        logger.info(f"代码标准化: {'有效' if is_format_normalized else '无效'}")
    
    logger.info("\n测试完成")
    

if __name__ == "__main__":
    test_stock_codes_and_cache() 