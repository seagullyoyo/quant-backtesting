#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略优化引擎
用于优化策略参数，寻找最佳参数组合
"""

import os
import itertools
import numpy as np
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

from quantitative_trading_system.utils.logger import get_logger
from quantitative_trading_system.strategy.backtesting.engine import BacktestEngine


class OptimizationEngine:
    """策略参数优化引擎"""
    
    def __init__(self, strategy, param_grid, start_date=None, end_date=None, 
                initial_capital=1000000, benchmark=None, data_frequency='daily'):
        """
        初始化优化引擎
        
        Args:
            strategy: 策略对象
            param_grid (dict): 参数网格，格式为 {param_name: [param_values]}
            start_date (str, optional): 回测开始日期，格式YYYY-MM-DD
            end_date (str, optional): 回测结束日期，格式YYYY-MM-DD
            initial_capital (float, optional): 初始资金
            benchmark (str, optional): 基准指数代码
            data_frequency (str, optional): 数据频率
        """
        self.logger = get_logger(self.__class__.__name__)
        self.strategy = strategy
        self.param_grid = param_grid
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.benchmark = benchmark
        self.data_frequency = data_frequency
        
        self.results = []
        self.best_params = None
        self.best_result = None
        
        self.logger.info(f"初始化策略优化引擎，策略: {strategy.name}")
        self.logger.info(f"参数网格: {param_grid}")
    
    def run_optimization(self, metric='sharpe_ratio', max_workers=None):
        """
        运行参数优化
        
        Args:
            metric (str, optional): 优化目标指标，如'sharpe_ratio', 'annual_return', 'max_drawdown'等
            max_workers (int, optional): 最大并行进程数. Defaults to None.
            
        Returns:
            dict: 优化结果
        """
        self.logger.info(f"开始参数优化，优化指标: {metric}")
        
        # 生成参数组合
        param_keys = list(self.param_grid.keys())
        param_values = list(self.param_grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        self.logger.info(f"参数组合总数: {len(param_combinations)}")
        
        # 并行执行回测
        self.results = []
        
        if max_workers and max_workers > 1:
            # 多进程并行执行
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for params in param_combinations:
                    param_dict = dict(zip(param_keys, params))
                    futures.append(
                        executor.submit(self._run_backtest_with_params, param_dict)
                    )
                
                for future in tqdm(as_completed(futures), total=len(futures), desc="优化进度"):
                    result = future.result()
                    if result:
                        self.results.append(result)
        else:
            # 单进程执行
            for params in tqdm(param_combinations, desc="优化进度"):
                param_dict = dict(zip(param_keys, params))
                result = self._run_backtest_with_params(param_dict)
                if result:
                    self.results.append(result)
        
        # 根据指标排序
        if self.results:
            # 对于最大回撤，越小越好，需要反向排序
            reverse = False if metric == 'max_drawdown' else True
            
            sorted_results = sorted(self.results, key=lambda x: x[metric], reverse=reverse)
            self.best_result = sorted_results[0]
            self.best_params = self.best_result['params']
            
            self.logger.info(f"优化完成，最佳参数: {self.best_params}")
            self.logger.info(f"最佳指标 {metric}: {self.best_result[metric]}")
            
            # 返回完整结果
            return {
                'best_params': self.best_params,
                'best_result': self.best_result,
                'all_results': self.results
            }
        else:
            self.logger.error("优化失败，没有有效结果")
            return None
    
    def _run_backtest_with_params(self, params):
        """
        使用指定参数运行回测
        
        Args:
            params (dict): 策略参数
            
        Returns:
            dict: 回测结果
        """
        try:
            # 创建策略的副本
            strategy_copy = self._clone_strategy()
            if not strategy_copy:
                return None
            
            # 设置参数
            strategy_copy.set_parameters(**params)
            
            # 创建回测引擎
            engine = BacktestEngine(
                strategy=strategy_copy,
                start_date=self.start_date,
                end_date=self.end_date,
                initial_capital=self.initial_capital,
                benchmark=self.benchmark,
                data_frequency=self.data_frequency
            )
            
            # 运行回测
            result = engine.run_backtest()
            
            if result:
                # 添加参数信息
                result['params'] = params
                return result
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"参数 {params} 回测失败: {str(e)}")
            return None
    
    def _clone_strategy(self):
        """
        创建策略的副本
        
        Returns:
            StrategyBase: 策略副本
        """
        try:
            strategy_class = self.strategy.__class__
            strategy_copy = strategy_class(
                name=self.strategy.name,
                author=self.strategy.author,
                description=self.strategy.description
            )
            return strategy_copy
            
        except Exception as e:
            self.logger.error(f"创建策略副本失败: {str(e)}")
            return None
    
    def save_results(self, filepath):
        """
        保存优化结果
        
        Args:
            filepath (str): 保存路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            if not self.results:
                self.logger.warning("没有优化结果可保存")
                return False
            
            # 将结果转换为DataFrame
            results_data = []
            for result in self.results:
                data = {
                    'total_return': result['total_return'],
                    'annual_return': result['annual_return'],
                    'volatility': result['volatility'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'max_drawdown': result['max_drawdown'],
                    'win_rate': result['win_rate'],
                    'final_value': result['final_portfolio_value']
                }
                # 添加参数
                for key, value in result['params'].items():
                    data[key] = value
                
                results_data.append(data)
            
            # 创建DataFrame
            df = pd.DataFrame(results_data)
            
            # 保存为CSV文件
            df.to_csv(filepath, index=False)
            
            self.logger.info(f"优化结果已保存到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存优化结果失败: {str(e)}")
            return False


def run_optimization(strategy_path, param_grid, start_date=None, end_date=None, 
                    initial_capital=None, benchmark=None, data_frequency='daily', 
                    metric='sharpe_ratio', max_workers=None):
    """
    运行策略参数优化的便捷函数
    
    Args:
        strategy_path (str): 策略路径或策略对象
        param_grid (dict): 参数网格，格式为 {param_name: [param_values]}
        start_date (str, optional): 回测开始日期
        end_date (str, optional): 回测结束日期
        initial_capital (float, optional): 初始资金
        benchmark (str, optional): 基准指数代码
        data_frequency (str, optional): 数据频率
        metric (str, optional): 优化目标指标
        max_workers (int, optional): 最大并行进程数
    
    Returns:
        dict: 优化结果
    """
    logger = get_logger("run_optimization")
    
    try:
        # 加载策略
        if isinstance(strategy_path, str):
            if os.path.isfile(strategy_path):
                # 从文件加载策略
                from quantitative_trading_system.strategy.base.strategy_base import StrategyBase
                strategy = StrategyBase.load(strategy_path)
                if not strategy:
                    logger.error(f"加载策略失败: {strategy_path}")
                    return None
            else:
                # 从模块加载策略
                import importlib
                import inspect
                
                try:
                    module_path, class_name = strategy_path.rsplit('.', 1)
                    module = importlib.import_module(module_path)
                    strategy_class = getattr(module, class_name)
                    strategy = strategy_class()
                except (ValueError, ImportError, AttributeError) as e:
                    logger.error(f"加载策略失败: {str(e)}")
                    return None
        else:
            # 直接使用传入的策略对象
            strategy = strategy_path
        
        # 创建优化引擎
        engine = OptimizationEngine(
            strategy=strategy,
            param_grid=param_grid,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            benchmark=benchmark,
            data_frequency=data_frequency
        )
        
        # 运行优化
        results = engine.run_optimization(metric=metric, max_workers=max_workers)
        
        # 保存结果
        if results:
            result_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'results')
            if not os.path.exists(result_dir):
                os.makedirs(result_dir)
            
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(result_dir, f"optimization_{strategy.name}_{timestamp}.csv")
            engine.save_results(filepath)
        
        return results
        
    except Exception as e:
        logger.error(f"运行优化失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None 