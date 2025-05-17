#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web服务器模块
提供Web界面和RESTful API
"""

import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from quantitative_trading_system.utils.logger import get_logger
from quantitative_trading_system.data.api.data_api import data_api
from quantitative_trading_system.strategy.backtesting.engine import run_backtest
from quantitative_trading_system.strategy.optimization.engine import run_optimization
from quantitative_trading_system.config.config import API_CONFIG


# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置日志
logger = get_logger('web_server')


@app.route('/')
def index():
    """主页"""
    return jsonify({
        'status': 'success',
        'message': '量化交易系统API服务运行正常',
        'version': '0.1.0'
    })


@app.route('/api/data/price', methods=['GET'])
def get_price():
    """获取股票价格数据API"""
    try:
        # 获取参数
        symbols = request.args.get('symbols', '')
        symbols = symbols.split(',') if symbols else []
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        freq = request.args.get('freq', 'daily')
        
        if not symbols:
            return jsonify({
                'status': 'error',
                'message': '股票代码不能为空'
            }), 400
        
        # 调用DataAPI
        df = data_api.get_price(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            freq=freq
        )
        
        # 转换为JSON
        if df.empty:
            return jsonify({
                'status': 'warning',
                'message': '未找到数据',
                'data': []
            })
        
        # 处理日期时间格式
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
        if 'datetime' in df.columns:
            df['datetime'] = df['datetime'].astype(str)
        
        result = df.to_dict('records')
        
        return jsonify({
            'status': 'success',
            'message': '获取数据成功',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取价格数据失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取数据失败: {str(e)}'
        }), 500


@app.route('/api/backtest/run', methods=['POST'])
def run_backtest_api():
    """运行回测API"""
    try:
        # 获取请求体
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '请求数据不能为空'
            }), 400
        
        # 获取参数
        strategy_path = data.get('strategy')
        params = data.get('params', {})
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        initial_capital = data.get('initial_capital')
        benchmark = data.get('benchmark')
        
        if not strategy_path:
            return jsonify({
                'status': 'error',
                'message': '策略路径不能为空'
            }), 400
        
        # 导入策略
        try:
            import importlib
            module_path, class_name = strategy_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            strategy_class = getattr(module, class_name)
            strategy = strategy_class()
            
            # 设置参数
            if params:
                strategy.set_parameters(**params)
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'导入策略失败: {str(e)}'
            }), 500
        
        # 运行回测
        results = run_backtest(
            strategy_path=strategy,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            benchmark=benchmark
        )
        
        if not results:
            return jsonify({
                'status': 'error',
                'message': '回测失败，请查看日志'
            }), 500
        
        # 处理结果
        # 移除不可序列化的数据
        if 'portfolio_values' in results:
            results['portfolio_values'] = [float(v) for v in results['portfolio_values']]
        if 'daily_returns' in results:
            results['daily_returns'] = [float(v) for v in results['daily_returns']]
        
        return jsonify({
            'status': 'success',
            'message': '回测完成',
            'data': results
        })
        
    except Exception as e:
        logger.error(f"运行回测失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'运行回测失败: {str(e)}'
        }), 500


@app.route('/api/optimization/run', methods=['POST'])
def run_optimization_api():
    """运行优化API"""
    try:
        # 获取请求体
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '请求数据不能为空'
            }), 400
        
        # 获取参数
        strategy_path = data.get('strategy')
        param_grid = data.get('param_grid', {})
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        initial_capital = data.get('initial_capital')
        benchmark = data.get('benchmark')
        metric = data.get('metric', 'sharpe_ratio')
        
        if not strategy_path:
            return jsonify({
                'status': 'error',
                'message': '策略路径不能为空'
            }), 400
        
        if not param_grid:
            return jsonify({
                'status': 'error',
                'message': '参数网格不能为空'
            }), 400
        
        # 运行优化
        results = run_optimization(
            strategy_path=strategy_path,
            param_grid=param_grid,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            benchmark=benchmark,
            metric=metric
        )
        
        if not results:
            return jsonify({
                'status': 'error',
                'message': '优化失败，请查看日志'
            }), 500
        
        # 处理结果
        # 只返回最佳结果和参数
        response_data = {
            'best_params': results['best_params'],
            'best_metrics': {
                'total_return': results['best_result']['total_return'],
                'annual_return': results['best_result']['annual_return'],
                'sharpe_ratio': results['best_result']['sharpe_ratio'],
                'max_drawdown': results['best_result']['max_drawdown'],
                'win_rate': results['best_result']['win_rate']
            }
        }
        
        return jsonify({
            'status': 'success',
            'message': '优化完成',
            'data': response_data
        })
        
    except Exception as e:
        logger.error(f"运行优化失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'运行优化失败: {str(e)}'
        }), 500


def start_web_server(host=None, port=None, debug=None):
    """
    启动Web服务器
    
    Args:
        host (str, optional): 主机地址. Defaults to None.
        port (int, optional): 端口号. Defaults to None.
        debug (bool, optional): 是否启用调试模式. Defaults to None.
    """
    # 获取配置
    config = API_CONFIG.get('web_server', {})
    host = host or config.get('host', '0.0.0.0')
    port = port or config.get('port', 8080)  # 修改默认端口为8080，避免与Mac的AirPlay服务冲突
    debug = debug if debug is not None else config.get('debug', False)
    
    logger.info(f"启动Web服务器，地址: {host}:{port}, 调试模式: {debug}")
    
    # 启动服务器
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    start_web_server() 