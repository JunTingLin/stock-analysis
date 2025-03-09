import sqlite3
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class InventoryDAO:
    def __init__(self, db_path="data_prod.db"):
        self.db_path = db_path
        self._create_table()
    
    def _create_table(self):
        """建立 inventory 資料表，記錄庫存資料並以 account_id 作為外鍵"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                fetch_timestamp TEXT,
                create_timestamp TEXT DEFAULT (datetime('now','localtime')),
                stock_id TEXT,
                stock_name TEXT,
                quantity REAL,
                last_price REAL,
                pnl REAL,
                raw_data TEXT,
                FOREIGN KEY (account_id) REFERENCES account(account_id)
            );
        """)
        conn.commit()
        conn.close()
    
    def insert_inventory_data(self, account_id, inventory_data, fetch_timestamp=None):
        """
        將庫存資料寫入 inventory 表。
        
        Args:
            account_id (int): 對應 Account 資料表的 account_id。
            inventory_data (list[dict]): 庫存資料，每筆需包含 'stock_id', 'stock_name', 
                'quantity', 'last_price', 'pnl', 以及原始資料('raw_data')
            fetch_timestamp (str, optional): 資料擷取時間戳記，若未提供則使用當前時間
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 使用提供的擷取時間戳記或當前時間
        if fetch_timestamp is None:
            raise ValueError("fetch_timestamp cannot be None")
        batch_ts_str = fetch_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # 寫入新資料 (不刪除舊資料，以保留歷史記錄)
        for item in inventory_data:
            # 將原始資料轉為 JSON 字串儲存
            raw_data_json = json.dumps(item.get('raw_data', {}))
            
            cursor.execute("""
                INSERT INTO inventory (
                    account_id,
                    fetch_timestamp,
                    stock_id,
                    stock_name,
                    quantity,
                    last_price,
                    pnl,
                    raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id,
                batch_ts_str,
                item.get('stock_id'),
                item.get('stock_name'),
                item.get('quantity'),
                item.get('last_price'),
                item.get('pnl'),
                raw_data_json
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Inserted {len(inventory_data)} inventory records for account_id {account_id}")