import pandas as pd
import os
from finlab import data

class DataPersistenceManager:
    def __init__(self):
        self.company_info = data.get('company_basic_info')

    def update_current_portfolio_info_with_datetime(self, position_acc, datetime, pkl_path):
        if position_acc is None:
            return
        
        data_list = []
        for position in position_acc.position:
            stock_id = position['stock_id']
            stock_name = self.company_info.loc[self.company_info['stock_id'] == stock_id, '公司簡稱'].values[0]
            row = {
                "日期時間": datetime,
                "股票代號": stock_id,
                "股票名稱": stock_name,
                "持倉股數": float(position['quantity'])
            }
            data_list.append(row)
        
        current_portfolio_info = pd.DataFrame(data_list)
        
        if os.path.exists(pkl_path):
            existing_df = pd.read_pickle(pkl_path)
            updated_df = pd.concat([existing_df, current_portfolio_info], ignore_index=True)
            updated_df = updated_df.drop_duplicates(subset=["日期時間", "股票代號"], keep="last")
            updated_df = updated_df.reset_index(drop=True)
        else:
            updated_df = current_portfolio_info
        
        updated_df.to_pickle(pkl_path)
        return updated_df

    def update_next_portfolio_info_with_datetime(self, position_today, datetime, pkl_path):
        if position_today is None:
            return
        
        data_list = []
        for position in position_today.position:
            stock_id = position['stock_id']
            stock_name = self.company_info.loc[self.company_info['stock_id'] == stock_id, '公司簡稱'].values[0]
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

    def get_info_with_datetime(self, datetime, pkl_path):
        if os.path.exists(pkl_path):
            df = pd.read_pickle(pkl_path)
            filtered_df = df[df['日期時間'] == datetime]
            return filtered_df
        else:
            return pd.DataFrame()

    def update_financial_summary_with_datetime(self, acc, datetime, financial_summary_pkl_path):
        bank_balance = acc.get_cash()
        total_settlement_amount = acc.get_settlement()
        adjusted_bank_balance = bank_balance + total_settlement_amount

        # 資產總值
        total_assets = acc.get_total_balance()

        # 現股總市值
        total_market_value = total_assets - adjusted_bank_balance

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

    dpm = DataPersistenceManager(acc)

    import datetime
    d = datetime.date(2020, 1, 1)

    current_portfolio = dpm.update_current_portfolio_info_with_datetime(acc.get_position(), d, 'current_portfolio.pkl')
    print(current_portfolio)

    next_portfolio_info = dpm.update_next_portfolio_info_with_datetime(None, d, 'next_portfolio.pkl')
    print(next_portfolio_info)

    financial_summary = dpm.update_financial_summary_with_datetime(acc, d, 'financial_summary.pkl')
    print(financial_summary)
