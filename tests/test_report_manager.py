import os
import sys
from datetime import datetime
import pandas as pd

# 將專案根目錄添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from report_manager import ReportManager

# 建立假資料
def generate_fake_data():
    current_portfolio_today = pd.DataFrame({
        "datetime": [datetime(2024, 8, 18, 0, 42, 22)] * 3,
        "stock_id": ["2330", "2317", "6505"],
        "stock_name": ["台積電", "鴻海", "台塑化"],
        "quantity": [100, 200, 300],
        "close_price": [600, 100, 200],
        "market_value": [60000, 20000, 60000]
    })

    next_portfolio_today = pd.DataFrame({
        "datetime": [datetime(2024, 8, 18, 0, 42, 22)] * 3,
        "stock_id": ["2330", "2317", "6505"],
        "stock_name": ["台積電", "鴻海", "台塑化"],
        "adjusted_quantity": [110, 190, 310],
    })

    financial_summary_all = pd.DataFrame({
        "datetime": [
            datetime(2024, 8, 16, 0, 42, 22),
            datetime(2024, 8, 17, 0, 42, 22),
            datetime(2024, 8, 18, 0, 42, 22)
        ],
        "bank_balance": [50000, 60000, 70000],
        "settlements": [10000, 20000, 30000],
        "adjusted_bank_balance": [60000, 80000, 100000],
        "market_value": [100000, 120000, 140000],
        "total_assets": [160000, 200000, 240000]
    })

    financial_summary_today = pd.DataFrame({
        "datetime": [datetime(2024, 8, 18, 0, 42, 22)],
        "bank_balance": [50000],
        "settlements": [10000],
        "adjusted_bank_balance": [60000],
        "market_value": [100000],
        "total_assets": [160000]
    })

    order_status = pd.DataFrame({
        "action": ["BUY", "SELL"],
        "stock_id": ["2330", "2317"],
        "stock_name": ["台積電", "鴻海"],
        "quantity": [100, 200],
        "order_price": [600, 100],
        "extra_bid_pct": [0.05, 0.1],
        "order_condition": ["CASH", "MARGIN_TRADING"]
    })

    data_dict = {
        "current_portfolio_today": current_portfolio_today,
        "next_portfolio_today": next_portfolio_today,
        "financial_summary_all": financial_summary_all,
        "financial_summary_today": financial_summary_today,
        "order_status": order_status
    }

    return data_dict

# 測試 ReportManager 類
def test_report_manager():
    data_dict = generate_fake_data()

    # 創建 ReportManager 的實例
    report_manager = ReportManager(
        data_dict=data_dict,
        report_finlab_directory="output/report_finlab",
        report_final_directory="output/report_final",
        datetime=datetime(2024, 8, 18, 0, 42, 22),
        template_path="templates/report_template.html"
    )

    # 生成最終報表
    final_report_path = report_manager.save_final_report()

    print(f"Final report generated at: {final_report_path}")

# 執行測試
if __name__ == "__main__":
    test_report_manager()
