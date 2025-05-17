from quantitative_trading_system.data.api.data_api import data_api

# 获取平安银行的数据并保存
data = data_api.get_price(
    symbols='000001.SZ',
    start_date='2022-01-01',
    end_date='2022-12-31',
    freq='daily'
)

print(f"获取到数据条数: {len(data)}")