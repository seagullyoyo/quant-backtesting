import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# 常量定义
DATA_DIR = "historical_data"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# 策略绩效评估指标
def calculate_performance_metrics(returns):
    """计算策略绩效指标"""
    if len(returns) == 0:
        return {
            "总收益率": 0,
            "年化收益率": 0,
            "最大回撤": 0,
            "夏普比率": 0,
            "胜率": 0,
            "盈亏比": 0
        }
    
    # 累计收益
    total_return = (1 + returns).prod() - 1
    
    # 年化收益率 (假设252个交易日/年)
    annual_return = (1 + total_return) ** (252 / len(returns)) - 1
    
    # 最大回撤
    cumulative_returns = (1 + returns).cumprod()
    rolling_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    # 夏普比率 (假设无风险收益率为0)
    sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0
    
    # 胜率
    win_rate = len(returns[returns > 0]) / len(returns) if len(returns) > 0 else 0
    
    # 盈亏比
    profit_loss_ratio = abs(returns[returns > 0].mean() / returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 0
    
    return {
        "总收益率": total_return,
        "年化收益率": annual_return,
        "最大回撤": max_drawdown,
        "夏普比率": sharpe_ratio,
        "胜率": win_rate,
        "盈亏比": profit_loss_ratio
    }

def calculate_strategy_metrics(positions, prices, transaction_cost=0.001):
    """根据持仓计算策略收益和指标"""
    # 确保positions和prices的索引对齐
    positions = positions.reindex(prices.index).fillna(0)
    
    # 计算每日收益
    daily_returns = prices.pct_change()
    
    # 策略收益 = 昨日持仓 * 今日收益
    strategy_returns = positions.shift(1) * daily_returns
    strategy_returns = strategy_returns.fillna(0)
    
    # 计算交易成本
    trades = positions.diff().abs() * transaction_cost
    strategy_returns = strategy_returns - trades
    
    # 计算累计收益
    cum_returns = (1 + strategy_returns).cumprod() - 1
    
    # 计算绩效指标
    metrics = calculate_performance_metrics(strategy_returns)
    
    return {
        "daily_returns": strategy_returns,
        "cumulative_returns": cum_returns,
        "metrics": metrics
    }

# 加载数据
def load_stock_data(stock_code, period):
    """加载指定股票和时期的数据"""
    filepath = os.path.join(DATA_DIR, f"{stock_code}_{period}.csv")
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        return None
    
    # 读取数据
    df = pd.read_csv(filepath, encoding='utf-8')
    df['日期'] = pd.to_datetime(df['日期'])
    df.set_index('日期', inplace=True)
    
    return df

# 基础策略类
class TradingStrategy:
    def __init__(self, name, params=None):
        self.name = name
        self.params = params if params is not None else {}
        
    def generate_signals(self, data):
        """生成交易信号，返回一个Series，值为1(做多)、-1(做空)或0(不操作)"""
        raise NotImplementedError("子类必须实现此方法")

# 均线交叉策略
class MovingAverageCrossStrategy(TradingStrategy):
    def __init__(self, short_window=5, long_window=20):
        super().__init__("均线交叉策略", {"短期窗口": short_window, "长期窗口": long_window})
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data):
        """使用短期和长期均线交叉生成信号"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算短期和长期移动平均线
        data['短期均线'] = data['收盘'].rolling(window=self.short_window, min_periods=1).mean()
        data['长期均线'] = data['收盘'].rolling(window=self.long_window, min_periods=1).mean()
        
        # 生成交易信号
        signals[data['短期均线'] > data['长期均线']] = 1  # 金叉做多
        signals[data['短期均线'] < data['长期均线']] = -1  # 死叉做空
        
        return signals

# 突破策略
class BreakoutStrategy(TradingStrategy):
    def __init__(self, window=20):
        super().__init__("突破策略", {"窗口": window})
        self.window = window
    
    def generate_signals(self, data):
        """使用价格突破前N天高点/低点生成信号"""
        signals = pd.Series(index=data.index, data=0)
        
        # 计算过去N天的最高价和最低价
        data['滚动最高价'] = data['最高'].rolling(window=self.window).max()
        data['滚动最低价'] = data['最低'].rolling(window=self.window).min()
        
        # 向前移动一天，避免使用未来数据
        data['前期最高价'] = data['滚动最高价'].shift(1)
        data['前期最低价'] = data['滚动最低价'].shift(1)
        
        # 生成交易信号
        signals[(data['最高'] > data['前期最高价']) & (data['前期最高价'].notnull())] = 1  # 突破前期高点做多
        signals[(data['最低'] < data['前期最低价']) & (data['前期最低价'].notnull())] = -1  # 跌破前期低点做空
        
        return signals

def run_backtest(strategy, data, initial_capital=100000.0):
    """运行回测"""
    # 生成信号
    signals = strategy.generate_signals(data)
    
    # 计算策略表现
    prices = data['收盘']
    result = calculate_strategy_metrics(signals, prices)
    
    # 添加策略名称和参数
    result['strategy_name'] = strategy.name
    result['strategy_params'] = strategy.params
    
    return result

def plot_equity_curve(results, title="策略表现"):
    """绘制权益曲线"""
    plt.figure(figsize=(12, 6))
    for strategy_name, result in results.items():
        plt.plot(result['cumulative_returns'], label=strategy_name)
    
    plt.title(title)
    plt.xlabel("日期")
    plt.ylabel("累计收益")
    plt.legend()
    plt.grid(True)
    
    # 保存图像
    plt.savefig(os.path.join(RESULTS_DIR, f"{title.replace(' ', '_')}.png"))
    plt.close()

def run_and_evaluate_strategies(stock_code, train_period, test_period, strategies):
    """执行策略评估流程"""
    # 加载训练和测试数据
    train_data = load_stock_data(stock_code, train_period)
    test_data = load_stock_data(stock_code, test_period)
    
    if train_data is None or test_data is None:
        print(f"无法加载 {stock_code} 的数据")
        return None
    
    # 训练期结果
    train_results = {}
    for strategy in strategies:
        print(f"在训练集上运行 {strategy.name}...")
        result = run_backtest(strategy, train_data.copy())
        train_results[strategy.name] = result
    
    # 测试期结果
    test_results = {}
    for strategy in strategies:
        print(f"在测试集上运行 {strategy.name}...")
        result = run_backtest(strategy, test_data.copy())
        test_results[strategy.name] = result
    
    # 输出结果
    print("\n训练期(2022-2023)策略表现:")
    for strategy_name, result in train_results.items():
        metrics = result['metrics']
        print(f"\n{strategy_name}:")
        print(f"  总收益率: {metrics['总收益率']:.2%}")
        print(f"  年化收益率: {metrics['年化收益率']:.2%}")
        print(f"  最大回撤: {metrics['最大回撤']:.2%}")
        print(f"  夏普比率: {metrics['夏普比率']:.2f}")
        print(f"  胜率: {metrics['胜率']:.2%}")
        print(f"  盈亏比: {metrics['盈亏比']:.2f}")
    
    print("\n测试期(2024)策略表现:")
    for strategy_name, result in test_results.items():
        metrics = result['metrics']
        print(f"\n{strategy_name}:")
        print(f"  总收益率: {metrics['总收益率']:.2%}")
        print(f"  年化收益率: {metrics['年化收益率']:.2%}")
        print(f"  最大回撤: {metrics['最大回撤']:.2%}")
        print(f"  夏普比率: {metrics['夏普比率']:.2f}")
        print(f"  胜率: {metrics['胜率']:.2%}")
        print(f"  盈亏比: {metrics['盈亏比']:.2f}")
    
    # 绘制权益曲线
    plot_equity_curve(train_results, title=f"{stock_code}_训练期策略表现")
    plot_equity_curve(test_results, title=f"{stock_code}_测试期策略表现")
    
    return {
        "train": train_results,
        "test": test_results
    } 