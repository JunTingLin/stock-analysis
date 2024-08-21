import os
import sys
import pandas as pd
from datetime import datetime

# 將專案根目錄添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from report_manager import ReportManager

# 建立假資料
def generate_fake_data():
    current_portfolio_today = pd.DataFrame({
        "日期時間": datetime(2024, 8, 18, 0, 42, 22),
        "股票代號": ["2330", "2317", "6505"],
        "股票名稱": ["台積電", "鴻海", "台塑化"],
        "持倉張數": [100, 200, 300]
    })

    next_portfolio_today = pd.DataFrame({
        "日期時間": datetime(2024, 8, 18, 0, 42, 22),
        "股票代號": ["2330", "2317", "6505"],
        "股票名稱": ["台積電", "鴻海", "台塑化"],
        "調整後張數": [110, 190, 310]
    })

    financial_summary_all = pd.DataFrame({
        "日期時間": [
            datetime(2024, 8, 18, 0, 42, 22),
            datetime(2024, 8, 19, 0, 42, 22),
            datetime(2024, 8, 20, 0, 42, 22)
        ],
        "銀行餘額": [50000, 60000, 70000],
        "銀行餘額(計入交割款)": [100000, 150000, 200000],
        "現股總市值": [1000000, 1100000, 1200000],
        "資產總值": [1100000, 1250000, 1400000]
    })

    data_dict = {
        "current_portfolio_today": current_portfolio_today,
        "next_portfolio_today": next_portfolio_today,
        "financial_summary_all": financial_summary_all
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
