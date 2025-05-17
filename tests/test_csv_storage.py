#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CSV存储和数据API
"""
import os
import sys
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantitative_trading_system.data.api.data_api import DataAPI

def test_data_api():
    """测试数据API"""
    print("\n========== 测试数据API ==========")
    
    # 创建数据API实例
    data_api = DataAPI()
    
    # 获取平安银行近30天的数据
    print("\n获取平安银行近30天的日K线数据:")
    df = data_api.get_price(
        symbols='000001.SZ',
        start_date='2024-04-01',
        end_date='2024-04-30',
        freq='daily'
    )
    
    # 打印数据形状
    print(f"数据形状: {df.shape}")
    
    # 打印前几行数据
    print("\n数据示例:")
    if not df.empty:
        print(df.head())
    else:
        print("无数据")
    
    # 检查数据是否已存储到CSV文件
    print("\n检查数据存储:")
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    csv_file = os.path.join(data_dir, 'daily', '000001.SZ_daily.csv')
    
    if os.path.exists(csv_file):
        print(f"CSV文件已创建: {csv_file}")
        # 读取CSV文件
        stored_df = pd.read_csv(csv_file)
        print(f"存储的数据形状: {stored_df.shape}")
    else:
        print(f"CSV文件未创建: {csv_file}")
        
if __name__ == "__main__":
    test_data_api() 