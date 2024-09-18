import re
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
    
    def process_order_status(self, log_filepath):
        order_status_list = []

        # 正規表示式匹配日誌行中的各個字段
        pattern = re.compile(
            r"(?P<action>BUY|SELL)\s+"
            r"(?P<stock_id>\d+)\s+X\s+"
            r"(?P<quantity>\d+\.\d+)\s+@\s+"
            r"(?P<order_price>[\d\.]+)\s+"
            r"(with extra bid (?P<extra_bid_pct>\d+\.\d+%)\s+)?"
            r"(?P<order_condition>CASH|MARGIN_TRADING|DAY_TRADING_LONG|SHORT_SELLING|DAY_TRADING_SHORT)"
        )

        with open(log_filepath, 'r', encoding='utf-8') as log_file:
            for line in log_file:
                match = pattern.search(line)
                if match:
                    stock_id = match.group("stock_id")
                    stock_name = self.company_info.loc[self.company_info['stock_id'] == stock_id, '公司簡稱'].values[0]
                    
                    order_status = {
                        "action": match.group("action"),
                        "stock_id": stock_id,
                        "stock_name": stock_name,
                        "quantity": float(match.group("quantity")),
                        "order_price": float(match.group("order_price")),
                        "extra_bid_pct": float(match.group("extra_bid_pct").rstrip('%')) / 100 if match.group("extra_bid_pct") else 0.0,
                        "order_condition": match.group("order_condition")
                    }
                    order_status_list.append(order_status)

        order_status_df = pd.DataFrame(order_status_list, columns=[
            "action", "stock_id", "stock_name", "quantity", "order_price", "extra_bid_pct", "order_condition"
        ])
        order_status_df = order_status_df.sort_values(by="stock_id").reset_index(drop=True)

        return order_status_df
    
    def process_special_order(self, log_filepath):
        special_order_list = []

        # 正規表示式匹配日誌行中的各個字段
        pattern = re.compile(
            r"(?P<action>買入|賣出)\s+"
            r"(?P<stock_id>\d+)\s+"
            r"(?P<quantity>\d+\.\d+)\s+張\s+-\s+總價約\s+"
            r"(?P<total_price>[\d,\.]+)"
        )

        with open(log_filepath, 'r', encoding='utf-8') as log_file:
            for line in log_file:
                match = pattern.search(line)
                if match:
                    stock_id = match.group("stock_id")
                    stock_name = self.company_info.loc[self.company_info['stock_id'] == stock_id, '公司簡稱'].values[0]

                    special_order = {
                        "action": "BUY" if match.group("action") == "買入" else "SELL",
                        "stock_id": stock_id,
                        "stock_name": stock_name,
                        "quantity": float(match.group("quantity")),
                    }
                    special_order_list.append(special_order)

        special_order_df = pd.DataFrame(special_order_list, columns=["action", "stock_id", "stock_name", "quantity"])

        return special_order_df



    def process_financial_summary(self, acc, datetime):
        bank_balance = acc.get_cash()
        settlements = acc.get_settlement()
        adjusted_bank_balance = bank_balance + settlements

        total_assets = acc.get_total_balance()
        market_value = total_assets - adjusted_bank_balance

        new_data = {
            "datetime": datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "bank_balance": bank_balance,
            "settlements": settlements,
            "adjusted_bank_balance": adjusted_bank_balance,
            "market_value": market_value,
            "total_assets": total_assets
        }

        return pd.DataFrame([new_data])


if __name__ == '__main__':
    # from config_loader import ConfigLoader
    # from authentication import Authenticator
    # config_loader = ConfigLoader()
    # config_loader.load_env_vars()
    # auth = Authenticator()
    # auth.login_finlab()
    # acc = auth.login_fugle()

    dp = DataProcessor()

    # import datetime
    # d = datetime.date(2020, 1, 1)

    # current_portfolio = dp.process_current_portfolio(acc, acc.get_position(), d)
    # print(current_portfolio)

    # next_portfolio_info = dp.process_next_portfolio(None, d)
    # print(next_portfolio_info)

    # financial_summary = dp.process_financial_summary(acc, d)
    # print(financial_summary)

    order_status = dp.process_order_status('logs/2024-08-24_15-32-12.log')
    print(order_status)