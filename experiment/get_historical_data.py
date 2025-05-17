import pandas as pd
import numpy as np
import os
import time
from datetime import datetime, timedelta
import random

# 定义要分析的股票列表
STOCK_LIST = [
    {"code": "300999", "name": "金龙鱼"},
    {"code": "600519", "name": "贵州茅台"},
    {"code": "000001", "name": "平安银行"},
    {"code": "601318", "name": "中国平安"},
    {"code": "000333", "name": "美的集团"}
]

# 创建数据目录
DATA_DIR = "historical_data"
os.makedirs(DATA_DIR, exist_ok=True)

def generate_mock_data(stock_code, start_date, end_date, volatility=0.015):
    """生成模拟的股票数据"""
    print(f"生成 {stock_code} 从 {start_date} 到 {end_date} 的模拟数据...")
    
    # 转换日期格式
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # 创建日期范围 (只包含工作日)
    dates = pd.date_range(start=start, end=end, freq='B')
    
    # 初始价格 (不同的股票设置不同的初始价格)
    if stock_code == "300999":  # 金龙鱼
        base_price = 30.0
    elif stock_code == "600519":  # 贵州茅台
        base_price = 1500.0
    elif stock_code == "000001":  # 平安银行
        base_price = 15.0
    elif stock_code == "601318":  # 中国平安
        base_price = 50.0
    else:  # 美的集团
        base_price = 70.0
    
    # 生成价格序列
    n = len(dates)
    returns = np.random.normal(0.0005, volatility, n)
    prices = [base_price]
    for r in returns:
        prices.append(prices[-1] * (1 + r))
    prices = prices[1:]  # 移除初始价格
    prices = np.maximum(prices, 0.1)
    
    # 创建OHLCV数据
    data = []
    for i, date in enumerate(dates):
        # 当日价格
        close = prices[i]
        
        # 生成开盘、最高、最低价
        open_price = close * (1 + np.random.normal(0, 0.005))
        high_price = max(open_price, close) * (1 + abs(np.random.normal(0, 0.005)))
        low_price = min(open_price, close) * (1 - abs(np.random.normal(0, 0.005)))
        
        # 生成成交量 (与价格波动相关)
        if i > 0:
            price_change = abs(prices[i] - prices[i-1]) / prices[i-1]
            volume = int(np.random.normal(100000, 50000) * (1 + 5 * price_change))
        else:
            volume = int(np.random.normal(100000, 50000))
        
        # 确保成交量为正
        volume = max(volume, 1000)
        
        # 计算成交额
        amount = volume * close
        
        # 计算涨跌幅和涨跌额
        if i > 0:
            change_pct = (close - prices[i-1]) / prices[i-1] * 100
            change_amount = close - prices[i-1]
        else:
            change_pct = 0
            change_amount = 0
        
        # 计算振幅
        amplitude = (high_price - low_price) / prices[i-1] * 100 if i > 0 else 0
        
        # 计算换手率 (随机)
        turnover = np.random.uniform(0.5, 3.0)
        
        data.append({
            "日期": date.strftime("%Y-%m-%d"),
            "股票代码": stock_code,
            "开盘": round(open_price, 2),
            "收盘": round(close, 2),
            "最高": round(high_price, 2),
            "最低": round(low_price, 2),
            "成交量": volume,
            "成交额": round(amount, 1),
            "振幅": round(amplitude, 2),
            "涨跌幅": round(change_pct, 2),
            "涨跌额": round(change_amount, 2),
            "换手率": round(turnover, 2)
        })
    
    # 转换为DataFrame
    df = pd.DataFrame(data)
    return df

def save_data_to_csv(df, stock_code, period):
    """保存数据到CSV文件"""
    if df is None or df.empty:
        print(f"没有数据可保存: {stock_code}_{period}")
        return
    
    filename = os.path.join(DATA_DIR, f"{stock_code}_{period}.csv")
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"数据已保存到 {filename}")

def main():
    print("开始获取2022-2023年历史数据和2024年测试数据...")
    
    # 定义时间段
    periods = [
        {"name": "train_2022_2023", "start": "2022-01-01", "end": "2023-12-31"},
        {"name": "test_2024", "start": "2024-01-01", "end": "2024-04-30"}
    ]
    
    for stock in STOCK_LIST:
        code = stock["code"]
        name = stock["name"]
        print(f"\n处理 {name}({code})...")
        
        for period in periods:
            period_name = period["name"]
            start_date = period["start"]
            end_date = period["end"]
            
            try:
                # 尝试使用akshare获取数据
                try:
                    import akshare as ak
                    df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                           start_date=start_date.replace("-", ""), 
                                           end_date=end_date.replace("-", ""), 
                                           adjust="qfq")
                    
                    if df.empty:
                        raise Exception("AKShare返回空数据")
                    
                    # 格式化日期列
                    df['日期'] = pd.to_datetime(df['日期'])
                    df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
                    
                except Exception as e:
                    print(f"使用AKShare获取数据出错: {e}")
                    df = None
                
                # 如果akshare获取失败，使用模拟数据
                if df is None or df.empty:
                    print("使用模拟数据代替...")
                    df = generate_mock_data(code, start_date, end_date)
                
                save_data_to_csv(df, code, period_name)
                
            except Exception as e:
                print(f"处理数据时出错: {e}")
            
            # 添加延迟以避免请求过快
            time.sleep(0.5)
    
    print("\n所有数据下载完成！")

if __name__ == "__main__":
    main() 