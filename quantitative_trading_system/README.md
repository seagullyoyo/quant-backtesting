# 量化交易系统

## 项目简介

这是一个完整的量化交易系统，提供从数据获取、策略开发、回测分析到实盘交易的全流程解决方案。系统采用模块化设计，各组件之间松耦合，便于扩展和维护。系统主要使用Python开发，依赖AKShare库获取中国股市数据。

## 系统架构

系统采用分层架构，分为以下几个主要模块：

- **数据层**：负责数据获取、存储和预处理
  - 数据抓取模块：通过AKShare获取股票数据
  - 数据存储模块：使用CSV文件存储历史数据
  - 数据API模块：提供统一的数据访问接口
  
- **策略层**：负责策略开发、回测和优化
  - 策略基类：提供所有策略的共同接口
  - 策略库：包含移动平均线交叉策略等预置策略
  - 回测引擎：在历史数据上模拟交易，评估策略性能
  - 优化引擎：寻找策略参数的最优组合
  
- **交易层**：负责订单管理和交易执行
  - 订单管理模块：创建和跟踪交易订单
  - 交易执行模块：执行实盘交易
  - 持仓管理模块：管理交易账户持仓
  
- **风控层**：负责风险管理和资金管理
  - 风险评估模块：评估投资组合风险
  - 风险控制模块：实施风险控制措施
  - 资金管理模块：优化资金配置
  
- **分析层**：负责绩效分析和报告生成
  - 绩效分析模块：计算各种绩效指标
  - 归因分析模块：分析交易策略的收益来源
  - 报告生成模块：生成回测报告
  
- **界面层**：负责用户交互和可视化展示
  - Web服务模块：提供RESTful API接口
  - 可视化模块：展示交易策略的运行结果

## 安装与使用

### 环境要求

- Python 3.9+
- 依赖包：参见 `requirements.txt`

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/quantitative_trading_system.git
cd quantitative_trading_system
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

### 使用示例

#### 数据获取

```python
from quantitative_trading_system.data.api.data_api import data_api

# 获取股票数据
df = data_api.get_price(
    symbols=['000001.SZ', '600519.SH'],
    start_date='2022-01-01',
    end_date='2022-12-31',
    freq='daily'
)
print(df.head())
```

#### 策略回测

```python
from quantitative_trading_system.strategy.library.moving_average_strategy import MovingAverageStrategy
from quantitative_trading_system.strategy.backtesting.engine import BacktestEngine

# 创建策略
strategy = MovingAverageStrategy()
strategy.set_parameters(
    symbols=['000001.SZ'],
    short_window=5,
    long_window=20
)

# 创建回测引擎
engine = BacktestEngine(
    strategy=strategy,
    start_date='2022-01-01',
    end_date='2022-12-31',
    initial_capital=1000000
)

# 运行回测
results = engine.run_backtest()

# 打印结果
print(f"总收益率: {results['total_return']:.2%}")
print(f"年化收益率: {results['annual_return']:.2%}")
print(f"最大回撤: {results['max_drawdown']:.2%}")
print(f"夏普比率: {results['sharpe_ratio']:.2f}")
```

#### 实盘交易

```python
from quantitative_trading_system.strategy.library.moving_average_strategy import MovingAverageStrategy
from quantitative_trading_system.trading.execution.engine import start_live_trading

# 创建策略
strategy = MovingAverageStrategy()
strategy.set_parameters(
    symbols=['000001.SZ'],
    short_window=5,
    long_window=20
)

# 启动实盘交易
engine = start_live_trading(strategy)
```

## 项目结构

```
quantitative_trading_system/
├── config/                   # 配置文件
├── data/                     # 数据相关模块
│   ├── fetcher/              # 数据抓取模块
│   ├── processor/            # 数据处理模块
│   ├── storage/              # 数据存储模块
│   └── api/                  # 数据访问接口
├── strategy/                 # 策略相关模块
│   ├── base/                 # 策略基类
│   ├── library/              # 预置策略库
│   ├── backtesting/          # 回测引擎
│   └── optimization/         # 优化引擎
├── trading/                  # 交易相关模块
│   ├── order/                # 订单管理模块
│   ├── execution/            # 交易执行模块
│   ├── position/             # 持仓管理模块
│   └── adapter/              # 交易接口适配器
├── risk/                     # 风控相关模块
│   ├── assessment/           # 风险评估模块
│   ├── control/              # 风险控制模块
│   ├── money/                # 资金管理模块
│   └── monitor/              # 监控警报模块
├── analysis/                 # 分析相关模块
│   ├── performance/          # 绩效分析模块
│   ├── attribution/          # 归因分析模块
│   ├── report/               # 报告生成模块
│   └── mining/               # 数据挖掘模块
├── interface/                # 界面相关模块
│   ├── web/                  # Web服务模块
│   ├── frontend/             # 前端应用模块
│   ├── visualization/        # 可视化模块
│   └── notification/         # 通知模块
├── utils/                    # 工具函数库
├── examples/                 # 示例代码
└── tests/                    # 测试代码
```

## 预置策略库

系统内置了多种常用交易策略，包括：

- 移动平均线交叉策略：当短期均线上穿/下穿长期均线时产生买入/卖出信号
- 相对强弱指标(RSI)策略：监测市场超买超卖状态，RSI低于30时买入，高于70时卖出
- 布林带策略：利用价格波动的统计特性，价格触及下轨时买入，触及上轨时卖出
- 动量策略：追踪价格趋势，买入过去表现强势的股票，卖出表现弱势的股票
- 更多策略持续开发中...

## 策略对比工具

系统提供了策略性能对比工具，可以在相同的历史数据和初始资金条件下比较不同策略的表现：

```bash
python -m quantitative_trading_system.examples.run_strategies_backtest_comparison
```

对比工具会输出各策略的关键性能指标，包括：
- 总收益率
- 年化收益率
- 最大回撤
- 夏普比率
- 波动率
- 胜率
- 盈亏比

同时生成直观的收益率对比图表，帮助用户选择最适合自己的交易策略。

## 运行模式

系统支持四种运行模式：

1. **web模式**：启动Web服务，提供API接口和可视化界面
   ```bash
   python main.py --mode web
   ```

2. **backtest模式**：运行策略回测，评估历史表现
   ```bash
   python main.py --mode backtest --strategy strategies/ma_cross.py
   ```

3. **optimization模式**：优化策略参数，寻找最优配置
   ```bash
   python main.py --mode optimization --strategy strategies/ma_cross.py
   ```

4. **live_trading模式**：执行实盘交易
   ```bash
   python main.py --mode live_trading --strategy strategies/ma_cross.py
   ```

## 主要依赖

系统主要依赖包括：
- akshare：获取A股市场数据
- pandas：数据处理与分析
- numpy：数学计算
- flask：Web服务框架
- matplotlib：数据可视化
- scipy：科学计算

## 当前状态和待完成工作

### 已完成内容

1. **系统架构**：整体框架已经设计并实现
2. **数据获取**：通过AKShare实现A股数据获取功能
3. **数据存储**：实现了CSV格式的数据存储方案，替代了HDF5存储
4. **策略开发框架**：完成了策略基类设计
5. **示例策略**：实现了移动平均线交叉策略
6. **回测引擎**：完成了历史数据回测功能
7. **Web API**：基于Flask实现了RESTful API接口

### 待完成工作

1. **Web前端开发**：
   - 需要开发Web前端页面，目前只有空的templates和static目录
   - 实现策略交互配置界面
   - 实现回测结果可视化展示

2. **实盘交易接口**：
   - 完善实盘交易执行模块
   - 对接实际券商交易接口

3. **更多策略实现**：
   - 添加更多预置策略，如布林带、MACD等
   - 实现策略组合功能

4. **测试完善**：
   - 增加单元测试覆盖率
   - 进行系统压力测试和性能优化

5. **数据扩展**：
   - 增加基本面数据获取
   - 增加宏观经济数据支持
   - 增加板块和行业数据

6. **风控系统**：
   - 实现完整的风险控制模块
   - 添加实时风险监控和预警功能

7. **文档完善**：
   - 编写详细的API文档
   - 编写用户使用手册和开发指南

## 开发建议

### 优先级建议

1. **完成Web前端**：这是提升用户体验的关键
2. **添加更多策略**：丰富预置策略库，提高系统实用性
3. **完善风控模块**：风险控制是量化交易的核心
4. **对接实盘交易**：实现真实的交易执行功能
5. **性能优化**：提升系统在大数据量下的处理速度

### 项目改进方向

1. **前端开发**：优先完成Web前端开发，提供可视化界面，增强用户体验
2. **数据源多样化**：增加对多种数据源的支持，减少对单一数据源的依赖
3. **性能优化**：优化回测引擎性能，支持更大规模、更长时间周期的回测
4. **实盘交易**：建立完整的实盘交易流程，包括风控、执行和监控
5. **自动化部署**：添加Docker支持，简化部署和环境配置

## 贡献

欢迎提交问题或拉取请求。对于重大变更，请先打开一个问题讨论您想要更改的内容。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/) 