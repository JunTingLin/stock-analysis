import pandas as pd
import os
from finlab import data

class DataProcessor:
    def __init__(self):
        self.company_info = data.get('company_basic_info')

    def process_current_portfolio(self, position_acc, datetime):
        if position_acc is None:
            return pd.DataFrame()
        
        data_list = []
        for position in position_acc.position:
            stock_id = position['stock_id']
            stock_name = self.company_info.loc[self.company_info['stock_id'] == stock_id, '公司簡稱'].values[0]
            row = {
                "日期時間": datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "股票代號": stock_id,
                "股票名稱": stock_name,
                "持倉張數": float(position['quantity'])
            }
            data_list.append(row)
        
        return pd.DataFrame(data_list)

    def process_next_portfolio(self, position_today, datetime):
        if position_today is None:
            return pd.DataFrame()
        
        data_list = []
        for position in position_today.position:
            stock_id = position['stock_id']
            stock_name = self.company_info.loc[self.company_info['stock_id'] == stock_id, '公司簡稱'].values[0]
            row = {
                "日期時間": datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "股票代號": stock_id,
                "股票名稱": stock_name,
                "調整成張數": float(position['quantity'])
            }
            data_list.append(row)
        
        return pd.DataFrame(data_list)

    def process_financial_summary(self, acc, datetime):
        bank_balance = acc.get_cash()
        total_settlement_amount = acc.get_settlement()
        adjusted_bank_balance = bank_balance + total_settlement_amount

        total_assets = acc.get_total_balance()
        total_market_value = total_assets - adjusted_bank_balance

        new_data = {
            "日期時間": datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "銀行餘額": bank_balance,
            "交割款加總": total_settlement_amount,
            "銀行餘額(計入交割款)": adjusted_bank_balance,
            "現股總市值": total_market_value,
            "資產總值": total_assets
        }

        return pd.DataFrame([new_data])
    


if __name__ == '__main__':
    from authentication import check_env_vars, login_fugle
    check_env_vars()
    acc = login_fugle()

    dp = DataProcessor()

    import datetime
    d = datetime.date(2020, 1, 1)

    current_portfolio = dp.process_current_portfolio(acc.get_position(), d)
    print(current_portfolio)

    next_portfolio_info = dp.process_next_portfolio(acc.get_position(), d)
    print(next_portfolio_info)

    financial_summary = dp.process_financial_summary(acc, d)
    print(financial_summary)
