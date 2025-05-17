#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行移动平均线策略回测的示例脚本
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(project_root))

from quantitative_trading_system.strategy.library.moving_average_strategy import MovingAverageStrategy
from quantitative_trading_system.strategy.backtesting.engine import BacktestEngine
from quantitative_trading_system.config.config import STRATEGY_CONFIG


def run_ma_strategy_backtest():
    """运行移动平均线策略回测"""
    # 创建策略实例
    strategy = MovingAverageStrategy(
        name="MA交叉策略回测示例",
        author="Quant Team"
    )
    
    # 从配置文件获取股票列表
    stock_lists = STRATEGY_CONFIG.get('backtest_stock_list', {})
    blue_chips = stock_lists.get('blue_chips', ['000001.SZ'])
    
    # 设置策略参数
    strategy.set_parameters(
        symbols=blue_chips,  # 使用配置文件中的蓝筹股列表
        short_window=5,
        long_window=20,
        unit=1000
    )
    
    # 创建回测引擎
    engine = BacktestEngine(
        strategy=strategy,
        start_date='2022-01-01',
        end_date='2022-12-31',
        initial_capital=1000000,
        benchmark='000300.SH'
    )
    
    # 运行回测
    results = engine.run_backtest()
    
    if results:
        # 打印回测结果
        print("====== 回测结果 ======")
        print(f"策略名称: {strategy.name}")
        print(f"回测区间: 2022-01-01 至 2022-12-31")
        print(f"初始资金: 1,000,000 元")
        print(f"最终资金: {results['final_portfolio_value']:.2f} 元")
        print(f"总收益率: {results['total_return']:.2%}")
        print(f"年化收益率: {results['annual_return']:.2%}")
        print(f"基准收益率: {results['benchmark_return']:.2%}")
        print(f"Alpha: {results['alpha']:.4f}")
        print(f"Beta: {results['beta']:.4f}")
        print(f"夏普比率: {results['sharpe_ratio']:.4f}")
        print(f"最大回撤: {results['max_drawdown']:.2%}")
        print(f"胜率: {results['win_rate']:.2%}")
        print(f"交易笔数: {len(results['trades'])}")
        
        # 绘制回测结果图表
        plot_backtest_results(results)
    else:
        print("回测失败，请检查日志")


def plot_backtest_results(results):
    """
    绘制回测结果图表
    
    Args:
        results (dict): 回测结果
    """
    # 创建结果目录
    result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    # 转换数据
    portfolio_values = results['portfolio_values']
    dates = pd.date_range(start='2022-01-01', periods=len(portfolio_values), freq='B')
    
    # 创建图表
    plt.figure(figsize=(12, 8))
    
    # 绘制资产曲线
    plt.subplot(2, 1, 1)
    plt.plot(dates, portfolio_values, label='Portfolio Value')
    plt.title('MA Strategy Backtest Results (2022)')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.grid(True)
    plt.legend()
    
    # 绘制每日收益率
    daily_returns = results['daily_returns']
    plt.subplot(2, 1, 2)
    plt.bar(dates, daily_returns)
    plt.title('Daily Returns')
    plt.xlabel('Date')
    plt.ylabel('Return')
    plt.grid(True)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plt.savefig(os.path.join(result_dir, f'ma_backtest_result_{timestamp}.png'))
    
    # 显示图表
    plt.show()


if __name__ == "__main__":
    run_ma_strategy_backtest() 