#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化交易系统主入口文件

本文件是量化交易系统的主入口点，提供了多种运行模式：
- web: 启动Web服务界面，用于可视化交易和配置
- backtest: 回测模式，对历史数据上的策略进行回测
- optimization: 优化模式，优化策略参数
- live_trading: 实盘交易模式，执行实时交易

使用示例:
1. 启动Web服务:
   python main.py --mode web

2. 运行策略回测:
   python main.py --mode backtest --strategy strategies/ma_cross.py

3. 参数优化:
   python main.py --mode optimization --strategy strategies/ma_cross.py

4. 实盘交易:
   python main.py --mode live_trading --strategy strategies/ma_cross.py --config config/live_config.py

5. 自定义日志级别:
   python main.py --mode backtest --strategy strategies/ma_cross.py --log_level DEBUG
"""

import os
import sys
import argparse
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantitative_trading_system.interface.web.server import start_web_server
from quantitative_trading_system.utils.logger import setup_logger


def parse_arguments():
    """
    解析命令行参数
    
    可用参数:
    --mode: 系统运行模式，可选值：web, backtest, optimization, live_trading
           web - 启动Web服务界面，用于可视化交易和配置
           backtest - 回测模式，在历史数据上测试策略性能
           optimization - 优化模式，寻找策略的最优参数
           live_trading - 实盘交易模式，执行实时交易
           
    --config: 配置文件路径，默认为'./config/config.py'
             可指定自定义配置文件，例如不同的交易账户配置、回测参数配置等
    
    --strategy: 策略名称或路径
               回测、优化和实盘交易模式下必须指定
               可以是预定义策略名称，也可以是自定义策略文件的路径
               
    --log_level: 日志级别，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
                DEBUG - 详细的调试信息
                INFO - 一般信息消息（默认）
                WARNING - 警告消息
                ERROR - 错误消息
                CRITICAL - 严重错误消息
    
    返回:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(description='股票量化交易系统')
    parser.add_argument('--mode', type=str, default='web',
                        choices=['web', 'backtest', 'optimization', 'live_trading'],
                        help='系统运行模式：web(启动Web界面), backtest(策略回测), optimization(参数优化), live_trading(实盘交易)')
    parser.add_argument('--config', type=str, default='./config/config.py',
                        help='配置文件路径，可指定自定义配置文件')
    parser.add_argument('--strategy', type=str, 
                        help='策略名称或路径，回测/优化/实盘交易模式必须指定')
    parser.add_argument('--log_level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='日志级别，DEBUG(详细调试), INFO(一般信息), WARNING(警告), ERROR(错误), CRITICAL(严重错误)')
    return parser.parse_args()


def main():
    """
    主函数
    
    根据命令行参数，启动系统的不同运行模式。
    web模式：启动Web服务，提供可视化界面
    backtest模式：运行策略回测，评估历史表现
    optimization模式：优化策略参数，寻找最优配置
    live_trading模式：执行实盘交易
    """
    args = parse_arguments()
    
    # 设置日志
    setup_logger(log_level=args.log_level)
    logger = logging.getLogger(__name__)
    logger.info("启动股票量化交易系统...")
    
    # 根据不同的运行模式启动系统
    if args.mode == 'web':
        logger.info("以Web服务模式启动系统")
        start_web_server()
    elif args.mode == 'backtest':
        if not args.strategy:
            logger.error("回测模式需要指定策略，使用--strategy参数")
            sys.exit(1)
        logger.info(f"以回测模式启动系统，使用策略: {args.strategy}")
        from quantitative_trading_system.strategy.backtesting.engine import run_backtest
        run_backtest(args.strategy)
    elif args.mode == 'optimization':
        if not args.strategy:
            logger.error("优化模式需要指定策略，使用--strategy参数")
            sys.exit(1)
        logger.info(f"以优化模式启动系统，优化策略: {args.strategy}")
        from quantitative_trading_system.strategy.optimization.engine import run_optimization
        run_optimization(args.strategy)
    elif args.mode == 'live_trading':
        if not args.strategy:
            logger.error("实盘交易模式需要指定策略，使用--strategy参数")
            sys.exit(1)
        logger.info(f"以实盘交易模式启动系统，使用策略: {args.strategy}")
        from quantitative_trading_system.trading.execution.engine import start_live_trading
        start_live_trading(args.strategy)
    
    logger.info("系统正常退出")


if __name__ == "__main__":
    main() 