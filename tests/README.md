# 测试文件目录

此目录包含所有测试文件，用于测试系统的各个组件。

## 文件说明

1. **test_akshare_basic.py** - 测试 AKShare 基本功能，包括获取股票列表、股票信息、日线数据和分钟线数据
2. **test_akshare_direct.py** - 直接使用 AKShare 获取股票数据，测试基本的数据访问功能
3. **test_akshare_alternative.py** - 测试 AKShare 中可用的股票历史数据接口
4. **test_data_get_fixed.py** - 测试系统数据API，包括数据获取和存储功能
5. **test_csv_storage.py** - 测试 CSV 存储功能，用于替代 HDF5 存储

## 运行测试

在项目根目录下执行：

```bash
cd tests
python test_file_name.py
```

例如，要运行基本的 AKShare 测试：

```bash
cd tests
python test_akshare_basic.py
```

## 注意事项

- 所有测试文件都需要先确保已安装相关依赖包（akshare, pandas 等）
- 测试文件会自动创建数据存储目录和文件
- 部分测试可能需要网络连接以从数据源获取实时数据 