import os
import sys
import pandas as pd
import datetime

# 將專案根目錄添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from report_manager import ReportManager
from data_persistence_manager import DataPersistenceManager


# 模擬 financial_summary 的假數據
def generate_financial_summary():

    current_datetime = datetime.datetime.now()

    data = {
        "datetime": current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "bank_balance": 1000000,
        "settlement_sum": 50000,
        "adjusted_bank_balance": 1050000,
        "market_value": 2000000,
        "total_assets": 3050000
    }
    return pd.DataFrame([data])

def test_datapersistence_manager():
    # 初始化 SQLite 数据库路径
    db_path = "data.db"

    # 初始化 DataPersistenceManager
    dpm = DataPersistenceManager(db_path)

    # 模擬生成 financial_summary 的假数据
    financial_summary = generate_financial_summary()

    # 保存到 SQLite 数据库
    dpm.save_financial_summary(financial_summary)

    # 从 SQLite 数据库中读取并打印
    df = dpm.load_financial_summary()
    print(df)

if __name__ == "__main__":
    test_datapersistence_manager()
