import pandas as pd
from finlab import data

class DataProcessor:
    def __init__(self):
        self.company_info = data.get('company_basic_info')

    def process_current_portfolio(self, acc, position_acc, datetime):
        if position_acc is None:
            return pd.DataFrame()
        
        stock_ids = [position['stock_id'] for position in position_acc.position]
        stock_prices = acc.get_stocks(stock_ids)
        
        data_list = []
        for position in position_acc.position:
            stock_id = position['stock_id']
            stock_name = self.company_info.loc[self.company_info['stock_id'] == stock_id, '公司簡稱'].values[0]
            close_price = stock_prices[stock_id].close
            quantity = float(position['quantity'])
            market_value = close_price * quantity * 1000

            row = {
                "datetime": datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "stock_id": stock_id,
                "stock_name": stock_name,
                "quantity": quantity,
                "close_price": close_price,
                "market_value": market_value
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
                "datetime": datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "stock_id": stock_id,
                "stock_name": stock_name,
                "adjusted_quantity": float(position['quantity'])
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
            "datetime": datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "bank_balance": bank_balance,
            "total_settlement_amount": total_settlement_amount,
            "adjusted_bank_balance": adjusted_bank_balance,
            "total_market_value": total_market_value,
            "total_assets": total_assets
        }

        return pd.DataFrame([new_data])


if __name__ == '__main__':
    from config_loader import ConfigLoader
    from authentication import Authenticator
    config_loader = ConfigLoader()
    config_loader.load_env_vars()
    auth = Authenticator()
    auth.login_finlab()
    acc = auth.login_fugle()

    dp = DataProcessor()

    import datetime
    d = datetime.date(2020, 1, 1)

    current_portfolio = dp.process_current_portfolio(acc, acc.get_position(), d)
    print(current_portfolio)

    next_portfolio_info = dp.process_next_portfolio(None, d)
    print(next_portfolio_info)

    financial_summary = dp.process_financial_summary(acc, d)
    print(financial_summary)
