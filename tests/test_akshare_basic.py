#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 AKShare 基本功能
"""
import os
import sys
import akshare as ak
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_divider():
    print("\n" + "=" * 50 + "\n")

def test_stock_list():
    """测试获取股票列表"""
    print("获取股票列表...")
    try:
        # 获取股票列表
        stock_list = ak.stock_zh_a_spot_em()
        print(f"成功获取 {len(stock_list)} 只股票的信息")
        print("前5只股票:")
        print(stock_list.head())
        return True
    except Exception as e:
        print(f"获取股票列表出错: {str(e)}")
        return False

def test_stock_info():
    """测试获取股票信息"""
    print_divider()
    print("获取平安银行(000001.SZ)的信息...")
    try:
        # 获取个股信息
        stock_info = ak.stock_individual_info_em(symbol="000001")
        print("股票信息:")
        print(stock_info)
        return True
    except Exception as e:
        print(f"获取股票信息出错: {str(e)}")
        return False

def test_daily_data():
    """测试获取日线数据"""
    print_divider()
    print("获取平安银行(000001.SZ)的日线数据...")
    try:
        # 使用不同的日线数据获取函数
        df = ak.stock_zh_a_daily(symbol="000001", start_date="20240101", end_date="20240430", adjust="qfq")
        print(f"日线数据形状: {df.shape}")
        print("前5条记录:")
        print(df.head())
        return True
    except Exception as e:
        print(f"获取日线数据出错: {str(e)}")
        return False

def test_minute_data():
    """测试获取分钟线数据"""
    print_divider()
    print("获取平安银行(000001.SZ)的分钟线数据...")
    try:
        # 获取分钟线数据
        df = ak.stock_zh_a_minute(symbol="000001", period='1', adjust="qfq")
        print(f"分钟线数据形状: {df.shape}")
        print("前5条记录:")
        print(df.head())
        return True
    except Exception as e:
        print(f"获取分钟线数据出错: {str(e)}")
        return False

def test_akshare_version():
    """测试 AKShare 版本"""
    print_divider()
    print(f"AKShare 版本: {ak.__version__}")

if __name__ == "__main__":
    print("开始测试 AKShare 基本功能...")
    print_divider()
    
    # 测试各个功能
    test_stock_list()
    test_stock_info()
    test_daily_data()
    test_minute_data()
    test_akshare_version()
    
    print_divider()
    print("测试完成!") 