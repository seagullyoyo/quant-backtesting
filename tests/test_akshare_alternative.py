#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试查找 AKShare 可用的股票历史数据接口
"""
import os
import sys
import akshare as ak
import pandas as pd
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def find_stock_hist_methods():
    """查找 AKShare 可用的股票历史数据接口"""
    print("\n查找 AKShare 可用的股票历史数据接口...")
    
    # 获取 akshare 模块中的所有函数
    methods = dir(ak)
    
    # 使用正则表达式筛选可能的历史数据函数
    hist_methods = []
    for method in methods:
        if re.search(r'stock.*hist', method) or re.search(r'hist.*stock', method):
            hist_methods.append(method)
    
    # 打印找到的方法
    print(f"找到 {len(hist_methods)} 个可能的股票历史数据接口:")
    for i, method in enumerate(hist_methods, 1):
        print(f"{i}. {method}")
    
    return hist_methods

def test_hist_method(method_name):
    """测试指定的历史数据获取方法"""
    print(f"\n测试方法: {method_name}")
    try:
        # 获取方法引用
        method = getattr(ak, method_name)
        
        # 获取方法文档
        doc = method.__doc__
        if doc:
            print(f"文档: {doc.strip().split('.')[0]}...")
        
        # 尝试调用方法
        # 不同的方法参数不同，这里尝试几种常见参数组合
        try:
            # 尝试第一种参数组合
            df = method(symbol="000001")
            print(f"调用成功! 获取 {len(df)} 条数据")
            print("列: ", df.columns.tolist())
            print("前3行: ")
            print(df.head(3))
            return True
        except Exception as e1:
            print(f"参数1 失败: {str(e1)}")
            try:
                # 尝试第二种参数组合
                df = method(symbol="000001", period="daily")
                print(f"调用成功! 获取 {len(df)} 条数据")
                print("列: ", df.columns.tolist())
                print("前3行: ")
                print(df.head(3))
                return True
            except Exception as e2:
                print(f"参数2 失败: {str(e2)}")
                try:
                    # 尝试第三种参数组合
                    df = method(code="000001")
                    print(f"调用成功! 获取 {len(df)} 条数据")
                    print("列: ", df.columns.tolist())
                    print("前3行: ")
                    print(df.head(3))
                    return True
                except Exception as e3:
                    print(f"参数3 失败: {str(e3)}")
                    return False
            
    except Exception as e:
        print(f"测试方法出错: {str(e)}")
        return False


if __name__ == "__main__":
    print(f"AKShare 版本: {ak.__version__}")
    
    # 查找历史数据接口
    hist_methods = find_stock_hist_methods()
    
    # 测试前3个方法
    for method in hist_methods[:3]:
        test_hist_method(method) 