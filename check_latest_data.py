import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def check_latest_minute_data(symbol="300999", days_back=5):
    """
    检查最近几天的分钟级数据是否可以获取
    """
    today = datetime.today()
    print(f"今天日期: {today.strftime('%Y-%m-%d')}")
    
    for i in range(days_back):
        test_date = (today - timedelta(days=i)).strftime('%Y%m%d')
        print(f"\n正在检查 {test_date} 的分钟级数据...")
        
        try:
            df = ak.stock_zh_a_hist_min_em(symbol=symbol, period="1", 
                                       start_date=test_date, end_date=test_date)
            
            if df.empty:
                print(f"{test_date} 没有分钟级数据")
            else:
                print(f"{test_date} 成功获取到 {len(df)} 条分钟级数据")
                print("数据样例:")
                print(df.head(3))
                
                # 获取最早和最晚的时间
                min_time = df['时间'].min()
                max_time = df['时间'].max()
                print(f"数据时间范围: {min_time} 至 {max_time}")
                
                return test_date, df  # 找到数据后立即返回
                
        except Exception as e:
            print(f"获取 {test_date} 数据出错: {e}")
    
    print("\n未找到任何可用的分钟级数据")
    return None, None

def check_specific_date(symbol="300999", date_str="20250509"):
    """
    检查特定日期的分钟级数据
    """
    print(f"\n正在检查特定日期 {date_str} 的分钟级数据...")
    
    try:
        df = ak.stock_zh_a_hist_min_em(symbol=symbol, period="1", 
                                  start_date=date_str, end_date=date_str)
        
        if df.empty:
            print(f"{date_str} 没有分钟级数据")
            return None
        else:
            print(f"{date_str} 成功获取到 {len(df)} 条分钟级数据")
            print("数据样例:")
            print(df.head(3))
            
            # 获取最早和最晚的时间
            min_time = df['时间'].min()
            max_time = df['时间'].max()
            print(f"数据时间范围: {min_time} 至 {max_time}")
            
            return df
            
    except Exception as e:
        print(f"获取 {date_str} 数据出错: {e}")
        return None

def check_real_world_dates():
    """
    检查真实世界的不同日期
    """
    # 今年的日期
    year_2024 = "20240510"
    
    # 去年的日期
    year_2023 = "20230510"
    
    # 前年的日期
    year_2022 = "20220510"
    
    # 检查这些日期
    for date_str in [year_2024, year_2023, year_2022]:
        df = check_specific_date("300999", date_str)
        print("")

if __name__ == "__main__":
    # 先检查最新数据
    latest_date, df = check_latest_minute_data("300999", days_back=10)
    
    if latest_date:
        print(f"\n最新可获取的分钟级数据日期是: {latest_date}")
        
    # 再检查真实世界的日期
    print("\n========= 检查真实世界的历史日期 =========")
    check_real_world_dates()
    
    # 检查其他股票
    print("\n========= 检查其他股票代码 =========")
    # 检查贵州茅台
    check_specific_date("600519", "20240510")
    # 检查平安银行
    check_specific_date("000001", "20240510") 