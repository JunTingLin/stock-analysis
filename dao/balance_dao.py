import sqlite3
import logging
import datetime
from dao.account_dao import AccountDAO

logger = logging.getLogger(__name__)

class BalanceDAO:
    def __init__(self, db_path="data_prod.db"):
        self.db_path = db_path
        self.account_dao = AccountDAO(db_path)
        self._create_table()
    
    def _create_table(self):
        """建立 balance 資料表，記錄帳戶餘額資訊"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance (
                balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                bank_balance REAL,
                settlements REAL,
                adjusted_bank_balance REAL,
                market_value REAL,
                total_assets REAL,
                fetch_timestamp TEXT,
                created_timestamp TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (account_id) REFERENCES account (account_id)
            );
        """)
        conn.commit()
        conn.close()
    
    def get_account_id(self, account_name, broker_name, user_name):
        """
        依照帳戶名稱取得帳戶ID，若不存在則建立新帳戶
        
        Args:
            account_name (str): 帳戶名稱
            broker_name (str): 券商名稱
            user_name (str): 使用者名稱
            
        Returns:
            int: 帳戶ID
        """
        return self.account_dao.get_account_id(account_name, broker_name, user_name)
    
    def insert_balance(self, account_id, balance_data, fetch_timestamp=None):
        """
        插入餘額資料至資料庫
        
        Args:
            account_id (int): 帳戶ID
            balance_data (dict): 餘額資料，包含 bank_balance, settlements, adjusted_bank_balance, market_value, total_assets
            fetch_timestamp (datetime, optional): 紀錄時間戳記
            
        Returns:
            int: 新增資料的 balance_id
        """
        if fetch_timestamp is None:
            raise ValueError("timestamp cannot be None")
            
        batch_ts_str = fetch_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO balance (
                account_id, bank_balance, settlements, adjusted_bank_balance, 
                market_value, total_assets, fetch_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            account_id,
            balance_data['bank_balance'],
            balance_data['settlements'],
            balance_data['adjusted_bank_balance'],
            balance_data['market_value'],
            balance_data['total_assets'],
            batch_ts_str
        ))
        
        conn.commit()
        balance_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"Inserted balance record with ID {balance_id} for account {account_id}")
        return balance_id
    
    def get_latest_balance(self, account_id):
        """
        取得特定帳戶的最新餘額資料
        
        Args:
            account_id (int): 帳戶ID
            
        Returns:
            dict: 最新的餘額資料，若無資料則回傳 None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                balance_id, account_id, bank_balance, settlements, 
                adjusted_bank_balance, market_value, total_assets, 
                fetch_timestamp, created_timestamp 
            FROM balance 
            WHERE account_id = ? 
            ORDER BY fetch_timestamp DESC 
            LIMIT 1
        """, (account_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        columns = [
            'balance_id', 'account_id', 'bank_balance', 'settlements',
            'adjusted_bank_balance', 'market_value', 'total_assets',
            'fetch_timestamp', 'created_timestamp'
        ]
        
        return dict(zip(columns, row))
    
    def get_balance_history(self, account_id, start_date=None, end_date=None):
        """
        取得特定帳戶在指定日期範圍內的餘額歷史資料
        
        Args:
            account_id (int): 帳戶ID
            start_date (str, optional): 開始日期 (YYYY-MM-DD)
            end_date (str, optional): 結束日期 (YYYY-MM-DD)
            
        Returns:
            list: 餘額歷史資料列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                balance_id, account_id, bank_balance, settlements, 
                adjusted_bank_balance, market_value, total_assets, 
                fetch_timestamp, created_timestamp 
            FROM balance 
            WHERE account_id = ?
        """
        params = [account_id]
        
        if start_date:
            query += " AND fetch_timestamp >= ?"
            params.append(f"{start_date} 00:00:00")
        
        if end_date:
            query += " AND fetch_timestamp <= ?"
            params.append(f"{end_date} 23:59:59")
            
        query += " ORDER BY fetch_timestamp ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        columns = [
            'balance_id', 'account_id', 'bank_balance', 'settlements',
            'adjusted_bank_balance', 'market_value', 'total_assets',
            'fetch_timestamp', 'created_timestamp'
        ]
        
        balance_history = [dict(zip(columns, row)) for row in rows]
        conn.close()
        
        return balance_history