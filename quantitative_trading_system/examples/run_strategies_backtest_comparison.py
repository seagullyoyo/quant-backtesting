#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略回测比较示例
用于比较不同策略在相同条件下的回测结果
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from quantitative_trading_system.strategy.library.moving_average_strategy import MovingAverageStrategy
from quantitative_trading_system.strategy.library.rsi_strategy import RSIStrategy
from quantitative_trading_system.strategy.library.bollinger_bands_strategy import BollingerBandsStrategy
from quantitative_trading_system.strategy.library.momentum_strategy import MomentumStrategy
from quantitative_trading_system.strategy.backtesting.engine import BacktestEngine
from quantitative_trading_system.utils.logger import get_logger

# 创建日志记录器
logger = get_logger("strategy_comparison")

def normalize_stock_code(code):
    """
    标准化股票代码格式，确保缓存命中
    
    Args:
        code (str): 原始股票代码
    
    Returns:
        str: 标准化后的股票代码
    """
    # 去除前缀和后缀，只保留数字部分
    if code.startswith('sh') or code.startswith('sz'):
        code = code[2:]
    elif code.endswith('.SH') or code.endswith('.SZ'):
        code = code.split('.')[0]
    
    # 为股票代码添加标准后缀
    if code.startswith(('0', '2', '3')):
        return code + '.SZ'
    elif code.startswith(('6', '9')):
        return code + '.SH'
    elif code.startswith('000'):  # 指数代码特殊处理
        return code + '.SH' if code in ['000001', '000300'] else code + '.SZ'
    
    return code


def run_strategy_backtest(strategy, start_date, end_date, initial_capital=1000000, benchmark='000300.SH'):
    """
    运行单个策略回测
    
    Args:
        strategy: 策略对象
        start_date: 回测开始日期
        end_date: 回测结束日期
        initial_capital: 初始资金
        benchmark: 基准指数
        
    Returns:
        dict: 回测结果
    """
    # 创建回测引擎
    engine = BacktestEngine(
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        benchmark=normalize_stock_code(benchmark)  # 标准化基准代码
    )
    
    # 运行回测
    results = engine.run_backtest()
    
    return results


def compare_strategies(symbol='000001.SZ', start_date='2022-01-01', end_date='2022-12-31', 
                       initial_capital=1000000, benchmark='000300.SH'):
    """
    比较不同策略的回测结果
    
    Args:
        symbol: 回测股票代码
        start_date: 回测开始日期
        end_date: 回测结束日期
        initial_capital: 初始资金
        benchmark: 基准指数
        
    Returns:
        pd.DataFrame: 回测结果比较表
    """
    # 标准化股票代码和基准代码
    normalized_symbol = normalize_stock_code(symbol)
    normalized_benchmark = normalize_stock_code(benchmark)
    
    logger.info(f"使用标准化后的股票代码: {normalized_symbol}, 基准: {normalized_benchmark}")
    
    # 创建策略列表
    strategies = [
        {
            'name': '移动平均线策略',
            'instance': MovingAverageStrategy(),
            'params': {'symbols': [normalized_symbol], 'short_window': 5, 'long_window': 20}
        },
        {
            'name': 'RSI策略',
            'instance': RSIStrategy(),
            'params': {'symbols': [normalized_symbol], 'rsi_period': 14, 'overbought': 70, 'oversold': 30}
        },
        {
            'name': '布林带策略',
            'instance': BollingerBandsStrategy(),
            'params': {'symbols': [normalized_symbol], 'window': 20, 'num_std': 2.0}
        },
        {
            'name': '动量策略',
            'instance': MomentumStrategy(),
            'params': {'symbols': [normalized_symbol], 'lookback_period': 60, 'momentum_threshold': 5}
        }
    ]
    
    # 存储回测结果
    results = []
    
    # 运行每个策略的回测
    for strategy_info in strategies:
        print(f"运行 {strategy_info['name']} 回测...")
        
        # 设置策略参数
        strategy = strategy_info['instance']
        strategy.set_parameters(**strategy_info['params'])
        
        # 运行回测
        result = run_strategy_backtest(
            strategy=strategy,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            benchmark=normalized_benchmark
        )
        
        if result:
            # 添加策略名称
            result['strategy_name'] = strategy_info['name']
            results.append(result)
            
            # 打印结果
            print(f"策略: {strategy_info['name']}")
            print(f"总收益率: {result['total_return']:.2%}")
            print(f"年化收益率: {result['annual_return']:.2%}")
            print(f"最大回撤: {result['max_drawdown']:.2%}")
            print(f"夏普比率: {result['sharpe_ratio']:.2f}")
            print('-' * 50)
    
    # 创建结果DataFrame
    if results:
        df_results = pd.DataFrame(results)
        
        # 选择要展示的指标
        metrics = [
            'strategy_name', 'total_return', 'annual_return', 
            'max_drawdown', 'sharpe_ratio', 'volatility', 
            'win_rate', 'profit_factor'
        ]
        
        # 格式化百分比
        for col in ['total_return', 'annual_return', 'max_drawdown', 'volatility', 'win_rate']:
            if col in df_results.columns:
                df_results[col] = df_results[col] * 100
        
        # 选择并排序结果
        df_display = df_results[metrics].sort_values(by='sharpe_ratio', ascending=False)
        
        # 保存结果
        result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
        os.makedirs(result_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = os.path.join(result_dir, f'strategy_comparison_{timestamp}.csv')
        df_display.to_csv(result_file, index=False)
        
        print(f"结果已保存至: {result_file}")
        
        # 绘制收益率对比图
        plot_performance_comparison(results, start_date, end_date, normalized_symbol, result_dir, timestamp)
        
        return df_display
    
    return None


def plot_performance_comparison(results, start_date, end_date, symbol, result_dir, timestamp):
    """
    绘制策略收益率对比图
    
    Args:
        results: 回测结果列表
        start_date: 回测开始日期
        end_date: 回测结束日期
        symbol: 回测股票代码
        result_dir: 结果保存目录
        timestamp: 时间戳
    """
    plt.figure(figsize=(12, 8))
    
    for result in results:
        # 获取每日收益率数据
        if 'daily_returns' in result and 'dates' in result:
            # 计算累计收益率
            daily_returns = np.array(result['daily_returns'])
            cumulative_returns = (1 + daily_returns).cumprod() - 1
            
            # 绘制曲线
            plt.plot(result['dates'], cumulative_returns * 100, label=result['strategy_name'])
    
    plt.title(f'策略收益率对比 ({symbol}, {start_date} 至 {end_date})')
    plt.xlabel('日期')
    plt.ylabel('累计收益率 (%)')
    plt.grid(True)
    plt.legend()
    
    # 保存图表
    plot_file = os.path.join(result_dir, f'strategy_comparison_{timestamp}.png')
    plt.savefig(plot_file)
    plt.close()
    
    print(f"对比图已保存至: {plot_file}")


if __name__ == "__main__":
    # 设置回测参数
    symbol = '000001'  # 平安银行，使用纯数字代码格式
    start_date = '2022-01-01'
    end_date = '2022-12-31'
    initial_capital = 1000000
    benchmark = '000300'  # 沪深300指数，使用纯数字代码格式
    
    # 运行策略比较
    result_df = compare_strategies(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        benchmark=benchmark
    )
    
    if result_df is not None:
        # 打印策略比较结果
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 120)
        print("\n策略性能比较:")
        print(result_df)
    else:
        print("未能生成有效的比较结果") 