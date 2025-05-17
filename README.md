# 量化交易回测系统

本系统是一个基于Python的量化交易回测框架，用于开发、测试和评估各种交易策略。

## 主要功能

- 数据获取：支持从多种数据源获取股票历史数据
- 策略开发：提供灵活的策略开发框架
- 回测引擎：高效的策略回测系统
- 绩效评估：多维度的策略评估指标

## 目录结构

```
quantitative_trading_system/
├── config/             # 配置文件
├── data/               # 数据模块
│   ├── api/            # 数据API
│   ├── fetcher/        # 数据获取器
│   └── storage/        # 数据存储
├── strategy/           # 策略模块
│   ├── base/           # 策略基类
│   ├── library/        # 策略库
│   └── backtesting/    # 回测相关
├── utils/              # 工具函数
└── examples/           # 示例脚本
```

## 支持的策略

系统当前实现了以下交易策略：

1. 移动平均线交叉策略
2. RSI超买超卖策略
3. 布林带策略
4. 动量策略

## 数据缓存与股票代码标准化

为了提高回测性能并避免重复下载数据，系统实现了两级缓存机制：

1. **内存缓存**：通过`lru_cache`装饰器实现，程序运行期间有效
2. **文件缓存**：以CSV文件形式存储在`data`目录，持久化存储

系统自动对股票代码进行标准化处理，确保不同格式的相同股票代码（如`000001`、`000001.SZ`、`sz000001`）使用相同的缓存文件。使用统一格式可以显著提高回测效率。

使用示例：
```python
# 在回测脚本中调用DataAPI时自动使用缓存
df = data_api.get_price(
    symbols='000001',    # 会自动标准化为'000001.SZ'
    start_date='2022-01-01',
    end_date='2022-12-31'
)
```

## 安装与使用

### 环境要求

- Python 3.7+
- 依赖包（见 requirements.txt）

### 安装

```bash
# 克隆仓库
git clone <repository-url>

# 安装依赖
pip install -r requirements.txt
```

### 使用示例

```python
from quantitative_trading_system.strategy.library.moving_average_strategy import MovingAverageStrategy
from quantitative_trading_system.strategy.backtesting.engine import run_backtest

# 创建策略
ma_strategy = MovingAverageStrategy()
ma_strategy.set_parameters(symbols=['000001.SZ'], short_window=5, long_window=20)

# 运行回测
results = run_backtest(
    strategy=ma_strategy,
    start_date='2022-01-01',
    end_date='2022-12-31',
    initial_capital=1000000
)

# 打印结果
print(f"总收益率: {results['total_return']:.2%}")
print(f"年化收益率: {results['annual_return']:.2%}")
print(f"最大回撤: {results['max_drawdown']:.2%}")
print(f"夏普比率: {results['sharpe_ratio']:.2f}")
``` 