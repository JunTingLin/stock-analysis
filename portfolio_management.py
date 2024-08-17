import logging
import pandas as pd
import os
from finlab import data

def update_current_portfolio_info_with_datetime(acc, datetime, pkl_path):
    inventories = acc.sdk.get_inventories()

    data = []
    for inventory in inventories:
        row = {
            "日期時間": datetime,
            "股票代號": inventory["stk_no"],
            "股票名稱": inventory["stk_na"],
            "庫存股數": float(inventory["cost_qty"]),
            "即時價格": float(inventory["price_now"]),
            "市值": float(inventory["value_now"])
        }
        data.append(row)
    
    current_portfolio_info = pd.DataFrame(data)

    if os.path.exists(pkl_path):
        existing_df = pd.read_pickle(pkl_path)
        updated_df = pd.concat([existing_df, current_portfolio_info], ignore_index=True)
        updated_df = updated_df.drop_duplicates(subset=["日期時間", "股票代號"], keep="last")
        updated_df = updated_df.reset_index(drop=True)
    else:
        updated_df = current_portfolio_info
    
    updated_df.to_pickle(pkl_path)

    return updated_df

def update_next_portfolio_info_with_datetime(position_today, datetime, pkl_path):
    # 取得公司基本資料，將 stock_id 映射為中文股票名稱
    company_info = data.get('company_basic_info')
    
    data_list = []
    for position in position_today.position:
        stock_id = position['stock_id']
        stock_name = company_info.loc[company_info['stock_id'] == stock_id, '公司簡稱'].values[0]
        row = {
            "日期時間": datetime,
            "股票代號": stock_id,
            "股票名稱": stock_name,
            "調整成股數": float(position['quantity']) 
        }
        data_list.append(row)
    
    next_portfolio_info = pd.DataFrame(data_list)
    
    if os.path.exists(pkl_path):
        existing_df = pd.read_pickle(pkl_path)
        updated_df = pd.concat([existing_df, next_portfolio_info], ignore_index=True)
        updated_df = updated_df.drop_duplicates(subset=["日期時間", "股票代號"], keep="last")
        updated_df = updated_df.reset_index(drop=True)
    else:
        updated_df = next_portfolio_info
    
    updated_df.to_pickle(pkl_path)

    return updated_df

import pandas as pd
import os

def get_portfolio_info_with_datetime(datetime, pkl_path):
    if os.path.exists(pkl_path):
        df = pd.read_pickle(pkl_path)
        filtered_df = df[df['日期時間'] == datetime]
        return filtered_df
    else:
        return pd.DataFrame()
    

def get_total_settlement_amount(acc, datetime):
    # 取得交割款資訊
    settlements = acc.sdk.get_settlements()
    excluded_date = datetime.strftime('%Y%m%d')
    
    # 加總 price，但排除 c_date 與傳入的 datetime 相同的記錄
    total_amount = sum(
        float(settlement['price'])
        for settlement in settlements
        if settlement['c_date'] != excluded_date
    )
    
    return total_amount

def update_financial_summary_with_datetime(current_portfolio_pkl_path, datetime, acc, financial_summary_pkl_path):
    bank_balance = acc.get_cash()
    total_settlement_amount = get_total_settlement_amount(acc, datetime)
    adjusted_bank_balance = bank_balance + total_settlement_amount

    # 取得現股總市值
    current_portfolio_df = get_portfolio_info_with_datetime(datetime, current_portfolio_pkl_path)
    total_market_value = current_portfolio_df['市值'].sum()

    # 計算資產總值
    total_assets = adjusted_bank_balance + total_market_value

    # 建立新的 DataFrame
    new_data = {
        "日期時間": datetime,
        "銀行餘額": bank_balance,
        "交割款加總": total_settlement_amount,
        "銀行餘額(計入交割款)": adjusted_bank_balance,
        "現股總市值": total_market_value,
        "資產總值": total_assets
    }
    new_df = pd.DataFrame([new_data])

    if os.path.exists(financial_summary_pkl_path):
        existing_df = pd.read_pickle(financial_summary_pkl_path)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        updated_df = updated_df.drop_duplicates(subset=["日期時間"], keep="last")
        updated_df = updated_df.reset_index(drop=True)
    else:
        updated_df = new_df

    updated_df.to_pickle(financial_summary_pkl_path)

    return updated_df

if __name__ == '__main__':
    from authentication import check_env_vars, login_fugle
    check_env_vars()
    acc = login_fugle()

    # import datetime
    # d = datetime.date(2020,1,1) 
    # current_portfolio =  update_current_portfolio_info_with_datetime(acc, d, 'current_portfolio.pkl')
    # print(current_portfolio)
    # financial_summary = update_financial_summary_with_datetime('current_portfolio.pkl', d, acc, 'financial_summary.pkl')
    # print(financial_summary)
    print(acc.sdk.get_inventories())
