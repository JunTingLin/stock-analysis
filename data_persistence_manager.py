import sqlite3
import pandas as pd
import os
import logging

class DataPersistenceManager:
    def __init__(self, db_path='data_prod.db'):
        self.db_path = db_path
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS financial_summary (
                    datetime TEXT PRIMARY KEY,
                    bank_balance REAL,
                    settlements REAL,
                    adjusted_bank_balance REAL,
                    market_value REAL,
                    total_assets REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS monthly_fund (
                    month TEXT PRIMARY KEY,
                    weight REAL,
                    total_assets REAL,
                    fund REAL
                )
            ''')
            conn.commit()

    def save_financial_summary_today(self, data):
        # 擷取資料中的日期部分
        target_date = pd.to_datetime(data['datetime'].values[0]).date()

        with sqlite3.connect(self.db_path) as conn:
            # 檢查資料庫是否已經存在同一天的資料
            query = f"SELECT * FROM financial_summary WHERE DATE(datetime) = '{target_date}'"
            existing_data = pd.read_sql_query(query, conn)

            if not existing_data.empty:
                logging.info(f"Financial summary for {target_date} already exists. Skipping save.")
            else:
                # 若同一天沒有資料，則保存帶有完整時間的datetime
                data.to_sql('financial_summary', conn, if_exists='append', index=False)
                logging.info(f"Financial summary for {target_date} saved with full datetime.")


    def save_finlab_report(self, report, report_save_path):
        dir_name = os.path.dirname(report_save_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        report.display(save_report_path=report_save_path)

    def save_monthly_fund(self, month, weight, total_assets, fund):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO monthly_fund (month, weight, total_assets, fund)
                VALUES (?, ?, ?, ?)
            ''', (month, weight, total_assets, fund))
            conn.commit()

    def load_financial_summary(self):
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql('SELECT * FROM financial_summary', conn)
        return df
    
    def load_financial_summary_today(self, target_datetime):
        target_date = target_datetime.date()

        with sqlite3.connect(self.db_path) as conn:
            # 根據日期部分進行查詢，返回當天所有資料（帶時間）
            query = f"SELECT * FROM financial_summary WHERE DATE(datetime) = '{target_date}'"
            df = pd.read_sql_query(query, conn)
            
        return df
    
    def load_financial_summary_first_of_month(self, target_date):
        with sqlite3.connect(self.db_path) as conn:
            query = f"""
                SELECT * FROM financial_summary
                WHERE strftime('%Y-%m', datetime) = '{target_date.strftime('%Y-%m')}'
                ORDER BY datetime ASC
                LIMIT 1
            """
            df = pd.read_sql_query(query, conn)
        return df

    def load_monthly_fund(self):
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query("SELECT * FROM monthly_fund", conn)
        return df
    
    def load_monthly_fund_for_month(self, month):
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM monthly_fund WHERE month = ?"
            df = pd.read_sql_query(query, conn, params=(month,))
        return df

    
    


if __name__ == "__main__":
    dpm = DataPersistenceManager()
    # dpm.save_monthly_fund('2024-09', 0.8, 120000, 96000)
    df = dpm.load_monthly_fund_for_month('2024-09')
    print(df)