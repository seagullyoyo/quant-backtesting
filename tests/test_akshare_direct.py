#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试AKShare数据获取
"""
import os
import sys
import akshare as ak
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接获取平安银行的数据
try:
    # 使用 stock_zh_a_hist 获取数据
    df = ak.stock_zh_a_hist(symbol="000001", period="daily", 
                          start_date="20240101", end_date="20240430", 
                          adjust="")
    
    # 打印原始列名
    print("原始列名:", df.columns.tolist())
    
    # 打印数据形状
    print(f"数据形状: {df.shape}")
    
    # 打印前几行数据
    print("\n数据示例:")
    print(df.head())
    
    # 添加标准化的股票代码列
    df['symbol'] = '000001.SZ'
    
    print("\n添加股票代码后:")
    print(df.head())
    
except Exception as e:
    print(f"获取数据出错: {str(e)}")
    
    # 尝试不同的参数组合
    try:
        print("\n尝试不同的参数组合...")
        df = ak.stock_zh_a_hist(symbol="000001")
        print(f"不提供日期参数，成功获取 {len(df)} 条数据")
        print(df.head())
    except Exception as e2:
        print(f"获取数据出错: {str(e2)}") 