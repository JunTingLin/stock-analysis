import sqlite3
import pandas as pd
import os

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
            conn.commit()

    def save_financial_summary(self, data):
        with sqlite3.connect(self.db_path) as conn:
            data.to_sql('financial_summary', conn, if_exists='append', index=False)

    def load_financial_summary(self):
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql('SELECT * FROM financial_summary', conn)
        return df

    def save_finlab_report(self, report, report_save_path):
        dir_name = os.path.dirname(report_save_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        report.display(save_report_path=report_save_path)

