#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "data_prod.db"

def fetch_realized_pnl_data():
    """
    從 transaction_history 讀取資料，並轉成 DataFrame
    回傳: DataFrame(columns=['date','stock_id','pnl'])
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
    SELECT c_date, stk_no, stk_na, make
    FROM transaction_history
    """
    rows = cursor.execute(query).fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["c_date", "stk_no", "stk_na", "make"])

    # c_date => datetime (假設 c_date 是 "YYYYMMDD" 格式)
    df["date"] = df["c_date"].apply(
        lambda x: datetime.strptime(x, "%Y%m%d") if x else None
    )

    # 合併股票代號+名稱
    df["stock_id"] = df["stk_no"] + " " + df["stk_na"]

    # 損益欄位 => float
    df["pnl"] = df["make"].astype(float)

    # 只留這三個欄位
    df = df[["date", "stock_id", "pnl"]]
    return df


def fetch_assets_data():
    """
    讀取 account_assets 內的每日資產資訊，轉成 DataFrame
    預期欄位:
      record_date, bank_balance, settlements, total_assets,
      adjusted_bank_balance, market_value
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
    SELECT record_date,
           bank_balance,
           settlements,
           total_assets,
           adjusted_bank_balance,
           market_value
    FROM account_assets
    ORDER BY record_date
    """
    rows = cursor.execute(query).fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=[
        "record_date",
        "bank_balance",
        "settlements",
        "total_assets",
        "adjusted_bank_balance",
        "market_value"
    ])

    # 將 record_date 轉成 datetime
    # 假設 record_date 格式是 YYYY-MM-DD
    df["date"] = pd.to_datetime(df["record_date"], format="%Y-%m-%d")

    # 整數或浮點格式
    for col in ["bank_balance", "settlements", "total_assets", "adjusted_bank_balance", "market_value"]:
        df[col] = df[col].astype(float)

    # 最後只保留想要的順序
    df = df[[
        "date",
        "bank_balance",
        "settlements",
        "total_assets",
        "adjusted_bank_balance",
        "market_value"
    ]]

    return df


def fetch_inventories_by_date(record_date):
    """
    從 inventories 資料表撈指定 record_date 的庫存彙總資料
    回傳 Pandas DataFrame: [id, record_date, stk_no, stk_na, value_mkt]
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
    SELECT id, record_date, stk_no, stk_na, value_mkt
    FROM inventories
    WHERE record_date = ?
    """
    rows = cursor.execute(query, (record_date,)).fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["id", "record_date", "stk_no", "stk_na", "value_mkt"])
    return df


def fetch_inventories_detail(inventories_id):
    """
    從 inventories_detail 資料表撈指定 inventories_id 的庫存明細
    回傳 DataFrame: [detail_id, inventories_id, buy_sell, price, qty, t_date, value_mkt]
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
    SELECT detail_id, inventories_id, buy_sell, price, qty, t_date, value_mkt
    FROM inventories_detail
    WHERE inventories_id = ?
    """
    rows = cursor.execute(query, (inventories_id,)).fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["detail_id", "inventories_id", "buy_sell", "price", "qty", "t_date", "value_mkt"])
    return df

def fetch_orders_by_date(order_date):
    """
    從 orders 資料表，依 order_date = ? 查詢
    回傳 DataFrame: [id, stk_no, stk_na, qty, limit_price, extra_bid_pct, buy_sell,
                     order_date, order_time]
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    sql = """
        SELECT id, stk_no, stk_na, qty,
               limit_price, extra_bid_pct, buy_sell,
               order_date, order_time
        FROM orders
        WHERE order_date = ?
        ORDER BY id
    """
    rows = cursor.execute(sql, (order_date,)).fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=[
        "id", "stk_no", "stk_na", "qty",
        "limit_price", "extra_bid_pct", "buy_sell",
        "order_date", "order_time"
    ])
    return df
