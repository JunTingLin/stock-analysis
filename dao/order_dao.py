import sqlite3
import logging

logger = logging.getLogger(__name__)

class OrderDAO:
    def __init__(self, db_path="data_prod.db"):
        self.db_path = db_path
        self._create_table()
    
    def _create_table(self):
        """建立 order_history 資料表，記錄下單紀錄並以 account_id 作為外鍵"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                order_timestamp TEXT,
                create_timestamp TEXT DEFAULT (datetime('now','localtime')),
                action TEXT,
                stock_id TEXT,
                stock_name TEXT,
                quantity REAL,
                price REAL,
                extra_bid_pct REAL,
                order_condition TEXT,
                FOREIGN KEY (account_id) REFERENCES account(account_id)
            );
        """)
        conn.commit()
        conn.close()
    
    def insert_order_logs(self, order_logs, account_id, order_timestamp):
        """
        將下單記錄寫入 order_history 表。
        
        Args:
            order_logs (list[dict]): 每筆訂單資料，包含 'action', 'stock_id', 'stock_name', 
                'quantity', 'price', 'extra_bid_pct', 'order_condition'
            account_id (int): 對應 Account 資料表的 account_id。
            order_timestamp (datetime.datetime): 批次時間，用於標記這次下單作業。
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 將批次時間轉為字串格式儲存 (ISO 格式比較普遍)
        batch_ts_str = order_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        for order in order_logs:
            cursor.execute("""
                INSERT INTO order_history (
                    account_id,
                    order_timestamp,
                    action,
                    stock_id,
                    stock_name,
                    quantity,
                    price,
                    extra_bid_pct,
                    order_condition
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id,
                batch_ts_str,
                order.get("action"),
                order.get("stock_id"),
                order.get("stock_name"),
                order.get("quantity"),
                order.get("price"),
                order.get("extra_bid_pct"),
                order.get("order_condition")
            ))
        conn.commit()
        conn.close()
        logger.info(f"Inserted {len(order_logs)} order logs into order_history")