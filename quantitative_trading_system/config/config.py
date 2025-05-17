"""
系统配置文件
"""

# 数据库配置
DATABASE_CONFIG = {
    'market_data': {
        'type': 'mongodb',
        'host': 'localhost',
        'port': 27017,
        'db_name': 'market_data'
    },
    'trade_data': {
        'type': 'mysql',
        'host': 'localhost',
        'port': 3306,
        'user': 'trader',
        'password': 'password',
        'db_name': 'trade_data'
    },
    'history_data': {
        'type': 'hdf5',
        'path': './data/storage/history_data'
    }
}

# API配置
API_CONFIG = {
    'web_server': {
        'host': '0.0.0.0',
        'port': 8080,  # 修改端口为8080，避免与Mac的AirPlay服务冲突
        'debug': False
    },
    'data_api': {
        'rate_limit': 100,  # 每分钟请求限制
        'cache_time': 300  # 缓存时间(秒)
    }
}

# 交易配置
TRADING_CONFIG = {
    'default_order_type': 'limit',
    'default_qty': 100,
    'retry_times': 3,
    'retry_interval': 1
}

# 风控配置
RISK_CONFIG = {
    'max_position_pct': 0.1,  # 单一持仓最大比例
    'max_drawdown': 0.15,  # 最大回撤限制
    'daily_loss_limit': 0.03,  # 日亏损限制
    'stop_loss_pct': 0.05  # 止损比例
}

# 日志配置
LOG_CONFIG = {
    'log_level': 'INFO',
    'log_dir': './logs',
    'max_log_file_size': 20 * 1024 * 1024,  # 20MB
    'backup_count': 5
}

# 数据源配置
DATA_SOURCE_CONFIG = {
    'default': 'akshare',
    'sources': {
        'akshare': {
            'enabled': True,
            'rate_limit': 200  # 每分钟请求限制
        },
        'tushare': {
            'enabled': True,
            'token': 'your_token_here',
            'rate_limit': 100
        },
        'wind': {
            'enabled': False,
            'token': 'your_token_here'
        }
    }
}

# 回测配置
BACKTEST_CONFIG = {
    'default_initial_capital': 1000000,
    'default_commission': 0.0003,  # 默认手续费
    'default_slippage': 0.0001,  # 默认滑点
    'benchmark': '000300.SH'  # 默认基准 - 沪深300
} 

# 策略配置
STRATEGY_CONFIG = {
    # 移动平均线策略配置
    'moving_average': {
        'symbols': ['000001.SZ'],  # 默认股票列表 - 平安银行
        'short_window': 5,         # 短期窗口
        'long_window': 20,         # 长期窗口
        'unit': 100                # 交易单位
    },
    # RSI策略配置
    'rsi': {
        'symbols': ['000001.SZ'],  # 默认股票列表
        'rsi_period': 14,          # RSI计算周期
        'overbought': 70,          # 超买阈值
        'oversold': 30,            # 超卖阈值
        'unit': 100                # 交易单位
    },
    # 布林带策略配置
    'bollinger_bands': {
        'symbols': ['000001.SZ'],  # 默认股票列表
        'window': 20,              # 移动平均窗口
        'num_std': 2.0,            # 标准差倍数
        'unit': 100                # 交易单位
    },
    # 动量策略配置
    'momentum': {
        'symbols': ['000001.SZ'],    # 默认股票列表
        'lookback_period': 60,       # 回溯周期
        'holding_period': 20,        # 持有周期
        'momentum_threshold': 5,     # 动量阈值（百分比）
        'unit': 100                  # 交易单位
    },
    # 回测用的多股票配置
    'backtest_stock_list': {
        'default': ['000001.SZ'],  # 平安银行
        'blue_chips': ['000001.SZ', '600519.SH', '000858.SZ'],  # 平安银行、贵州茅台、五粮液
        'tech': ['000063.SZ', '000725.SZ', '002230.SZ'],  # 中兴通讯、京东方A、科大讯飞
        'finance': ['600036.SH', '601166.SH', '601398.SH']  # 招商银行、兴业银行、工商银行
    }
}