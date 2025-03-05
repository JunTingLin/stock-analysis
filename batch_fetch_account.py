from datetime import datetime, timedelta
from authentication import Authenticator
from config_loader import ConfigLoader
from db import init_db, store_assets, store_inventories_and_details, store_transaction_and_details

def initialize_environment():

    config_loader = ConfigLoader()
    config_loader.load_env_vars()

    auth = Authenticator()
    auth.login_finlab()
    acc = auth._login_fugle()
    return acc

def get_and_store_transactions(acc):

    init_db()

    raw_transactions = acc.sdk.get_transactions("3M")
    if not raw_transactions:
        print("No transactions fetched.")
        return
    print("Transactions fetched successfully.")

    transactions_data = []
    for tx in raw_transactions:
        filtered = {
            "buy_sell": tx.get("buy_sell", ""),
            "c_date": tx.get("c_date", ""),
            "cost": tx.get("cost", "0"),
            "make": tx.get("make", "0"),
            "qty": tx.get("qty", "0"),
            "stk_na": tx.get("stk_na", ""),
            "stk_no": tx.get("stk_no", ""),
            "mat_dats": []
        }

        mat_dats = tx.get("mat_dats", [])
        for detail in mat_dats:
            filtered["mat_dats"].append({
                "buy_sell": detail.get("buy_sell", ""),
                "c_date": detail.get("c_date", ""),
                "make": detail.get("make", "0"),
                "price": detail.get("price", "0"),
                "qty": detail.get("qty", "0")
            })
        transactions_data.append(filtered)

    store_transaction_and_details(transactions_data)

def get_and_store_assets(acc):
    """
    1. 初始化 db (若尚未建表)
    2. 透過 acc 物件呼叫 SDK
       - bank_balance = acc.get_cash()
       - total_assets = acc.get_total_balance()
       - settlements = acc.get_settlement()
    3. 計算 adjusted_bank_balance = bank_balance + settlements
       計算 market_value = total_assets - adjusted_bank_balance
    4. 呼叫 store_assets(assets_data) 寫入資料庫
    """
    init_db()

    # 假設以下方法能抓到整數或浮點數
    bank_balance = acc.get_cash()            # 銀行餘額
    total_assets = acc.get_total_balance()   # 總資產(含股票市值)
    settlements = acc.get_settlement()       # 交割款
    print("Bank_balance, Total_assets, Settlements fetched successfully.")

    adjusted_bank_balance = bank_balance + settlements
    market_value = total_assets - adjusted_bank_balance

    # 以今日日期存檔 (若要指定別的日期可自行更改)
    record_date_str = datetime.now().strftime("%Y-%m-%d")

    assets_data = {
        "record_date": record_date_str,
        "bank_balance": bank_balance,
        "settlements": settlements,
        "total_assets": total_assets,
        "adjusted_bank_balance": adjusted_bank_balance,
        "market_value": market_value
    }

    store_assets(assets_data)


def get_and_store_inventories(acc):
    """
    1. init_db() 確保表存在
    2. 從 acc.sdk.get_inventories() 取得外層 & 內層資料
    3. 只保留外層 (stk_na, stk_no, value_mkt) + 內層 (buy_sell, price, qty, t_date, value_mkt)
    4. 呼叫 store_inventories_and_details() 寫入
    """
    init_db()

    raw_inventories = acc.sdk.get_inventories()
    if not raw_inventories:
        print("No inventories fetched.")
        # return
    print("Inventories fetched successfully.")

    # 假設想以今日日期存檔
    record_date_str = datetime.now().strftime("%Y-%m-%d")

    inventories_data = []
    for inv in raw_inventories:
        # 外層
        filtered = {
            "record_date": record_date_str,
            "stk_no": inv.get("stk_no", ""),
            "stk_na": inv.get("stk_na", ""),
            "value_mkt": inv.get("value_mkt", "0"),
            "stk_dats": []  # 放內層
        }

        # 內層
        detail_list = inv.get("stk_dats", [])
        for detail in detail_list:
            filtered["stk_dats"].append({
                "buy_sell": detail.get("buy_sell", ""),
                "price": detail.get("price", "0"),
                "qty": detail.get("qty", "0"),
                "t_date": detail.get("t_date", ""),
                "value_mkt": detail.get("value_mkt", "0")
            })

        inventories_data.append(filtered)

    # 寫入資料庫
    store_inventories_and_details(inventories_data)



def main():
    acc = initialize_environment()
    # get_and_store_transactions(acc)
    # get_and_store_assets(acc)
    get_and_store_inventories(acc)

if __name__ == "__main__":
    main()
