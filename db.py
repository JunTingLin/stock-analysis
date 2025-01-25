import sqlite3

DB_NAME = "data_prod.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 開啟外鍵檢查 (SQLite 預設可能是關閉的)
    cursor.execute("PRAGMA foreign_keys = ON;")

    create_history_table_sql = """
    CREATE TABLE IF NOT EXISTS transaction_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buy_sell TEXT,
        c_date TEXT,
        cost REAL,
        make REAL,
        qty INTEGER,
        stk_na TEXT,
        stk_no TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_history_table_sql)

    create_detail_table_sql = """
    CREATE TABLE IF NOT EXISTS transaction_detail (
        detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        history_id INTEGER,  -- 外鍵, 對應 transaction_history.id
        buy_sell TEXT,
        c_date TEXT,
        make REAL,
        price REAL,
        qty INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (history_id) REFERENCES transaction_history(id) ON DELETE CASCADE
    );
    """
    cursor.execute(create_detail_table_sql)

    create_assets_table_sql = """
    CREATE TABLE IF NOT EXISTS account_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_date TEXT,             -- 記錄日期 (建議儲存 YYYY-MM-DD 或其它格式)
        bank_balance REAL,            -- 銀行餘額
        settlements REAL,             -- 交割款
        total_assets REAL,            -- 帳戶總資產(含持股市值)
        adjusted_bank_balance REAL,   -- (銀行餘額 + 交割款)
        market_value REAL,            -- 股票部位市值 (total_assets - adjusted_bank_balance)
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_assets_table_sql)

    create_inventories_sql = """
    CREATE TABLE IF NOT EXISTS inventories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_date TEXT,         -- 紀錄日期 (若要存抓取日，或自訂)
        stk_no TEXT,              -- 股票代號
        stk_na TEXT,              -- 股票名稱
        value_mkt REAL,           -- 該庫存的市值(無假除權息)
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_inventories_sql)    

    create_inventories_detail_sql = """
    CREATE TABLE IF NOT EXISTS inventories_detail (
        detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        inventories_id INTEGER,  -- 外鍵, 對應 inventories.id
        buy_sell TEXT,
        price REAL,
        qty INTEGER,
        t_date TEXT,
        value_mkt REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (inventories_id) REFERENCES inventories(id) ON DELETE CASCADE
    );
    """
    cursor.execute(create_inventories_detail_sql)

    create_orders_sql = """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stk_no TEXT,          -- 股票代號
        stk_na TEXT,          -- 股票名稱
        qty INTEGER,          -- 股數
        limit_price REAL,     -- 委託價
        extra_bid_pct REAL,   -- 額外加/減 價的百分比
        buy_sell TEXT,        -- 買賣方向 (B / S)
        order_date TEXT,      -- 訂單日期 (YYYY-MM-DD)
        order_time TEXT,      -- 訂單時間 (HH:MM:SS)
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_orders_sql)   

    conn.commit()
    conn.close()

def store_transaction_and_details(transaction_data):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    insert_history_sql = """
    INSERT INTO transaction_history
    (buy_sell, c_date, cost, make, qty, stk_na, stk_no)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    insert_detail_sql = """
    INSERT INTO transaction_detail
    (history_id, buy_sell, c_date, make, price, qty)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    for row in transaction_data:
        history_tuple = (
            row.get("buy_sell", ""),
            row.get("c_date", ""),
            float(row.get("cost", 0)),
            float(row.get("make", 0)),
            int(row.get("qty", 0)),
            row.get("stk_na", ""),
            row.get("stk_no", "")
        )
        cursor.execute(insert_history_sql, history_tuple)
        
        history_id = cursor.lastrowid

        mat_dats_list = row.get("mat_dats", [])
        for detail in mat_dats_list:
            detail_tuple = (
                history_id,
                detail.get("buy_sell", ""),
                detail.get("c_date", ""),
                float(detail.get("make", 0)),
                float(detail.get("price", 0)),
                int(detail.get("qty", 0))
            )
            cursor.execute(insert_detail_sql, detail_tuple)
    
    conn.commit()
    conn.close()
    print("Insert history and details successfully.")

def store_assets(assets_data):
    """
    將每日資產資訊寫入 account_assets
    assets_data 預期包含:
      record_date, bank_balance, settlements,
      total_assets, adjusted_bank_balance, market_value
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    insert_assets_sql = """
    INSERT INTO account_assets
    (record_date, bank_balance, settlements, total_assets, adjusted_bank_balance, market_value)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    data_tuple = (
        assets_data.get("record_date", ""),
        float(assets_data.get("bank_balance", 0)),
        float(assets_data.get("settlements", 0)),
        float(assets_data.get("total_assets", 0)),
        float(assets_data.get("adjusted_bank_balance", 0)),
        float(assets_data.get("market_value", 0))
    )
    cursor.execute(insert_assets_sql, data_tuple)

    conn.commit()
    conn.close()
    print("Insert assets successfully.")


def store_inventories_and_details(inventories_data):
    """
    接收 get_inventories() 回傳的資料 (list of dict)，分別存入：
    - inventories: (stk_na, stk_no, value_mkt, record_date)
    - inventories_detail: (buy_sell, price, qty, t_date, value_mkt)，並以 inventories_id 作外鍵
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    insert_inventories_sql = """
    INSERT INTO inventories
    (record_date, stk_no, stk_na, value_mkt)
    VALUES (?, ?, ?, ?)
    """

    insert_inventories_detail_sql = """
    INSERT INTO inventories_detail
    (inventories_id, buy_sell, price, qty, t_date, value_mkt)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    for inv in inventories_data:
        # 1. 寫入外層資料 inventories
        record_date = inv.get("record_date", "")   # 你可以在 get_and_store_inventories 裡指定
        stk_no = inv.get("stk_no", "")
        stk_na = inv.get("stk_na", "")
        value_mkt = float(inv.get("value_mkt", 0))

        cursor.execute(insert_inventories_sql, (record_date, stk_no, stk_na, value_mkt))
        inventories_id = cursor.lastrowid  # 拿到剛插入的主鍵

        # 2. 寫入內層資料 inventories_detail
        stk_dats = inv.get("stk_dats", [])
        for detail in stk_dats:
            buy_sell = detail.get("buy_sell", "")
            price = float(detail.get("price", 0))
            qty = int(detail.get("qty", 0))
            t_date = detail.get("t_date", "")
            value_mkt_d = float(detail.get("value_mkt", 0))

            cursor.execute(insert_inventories_detail_sql, (
                inventories_id,
                buy_sell,
                price,
                qty,
                t_date,
                value_mkt_d
            ))

    conn.commit()
    conn.close()
    print("Insert inventories and details successfully.")


def store_orders(orders_data):
    """
    將多筆訂單 (list of dict) 寫入 orders 表。
    預期每個 dict 至少包含:
      stk_no, stk_na, qty, limit_price, extra_bid_pct, buy_sell,
      order_date, order_time
    其餘欄位如 'created_at' 由資料庫自動帶入。
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    insert_orders_sql = """
    INSERT INTO orders
    (stk_no, stk_na, qty, limit_price, extra_bid_pct, buy_sell, order_date, order_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    for row in orders_data:
        data_tuple = (
            row.get("stk_no", ""),
            row.get("stk_na", ""),
            int(row.get("qty", 0)),
            float(row.get("limit_price", 0)),
            float(row.get("extra_bid_pct", 0)),
            row.get("buy_sell", ""),
            row.get("order_date", ""),
            row.get("order_time", "")
        )
        cursor.execute(insert_orders_sql, data_tuple)

    conn.commit()
    conn.close()
    print("Insert orders successfully.")