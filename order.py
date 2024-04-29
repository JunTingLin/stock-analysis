from TibetanMastiff_TW_Strategy import TibetanMastiffTWStrategy
from finlab.online.fugle_account import FugleAccount
from finlab.online.order_executor import OrderExecutor, Position
import os
import configparser
import pandas as pd
from decimal import Decimal
import logger_config
import logging

# 設置日誌
logger_config.setup_logging()

# 初始化策略
strategy = TibetanMastiffTWStrategy()
report = strategy.run_strategy()
close = strategy.get_close_prices()

# 讀取設定檔
config = configparser.ConfigParser()
config_file_name = 'config.simulation.ini'
config.read(config_file_name)

os.environ['FUGLE_CONFIG_PATH'] = config_file_name
os.environ['FUGLE_MARKET_API_KEY'] = config['FUGLE_MARKET']['FUGLE_MARKET_API_KEY']
acc = FugleAccount()

# 執行交易邏輯
fund = 100000 * 0.8  # 設置資金為現金的80%
print(f"當前帳戶現金為{acc.get_cash()}")

acc_position = acc.get_position()
print(f"當前帳戶目前持倉為{acc_position.position}")
current_ids = set(p['stock_id'] for p in acc_position.position)

# 獲取由report物件生成的今日持倉狀態
position_today = Position.from_report(report, fund, odd_lot=True)
new_ids = set(p['stock_id'] for p in position_today.position)

# 檢查今天是否為月初第一天，月初第一天確定換股調整
today = pd.Timestamp.now().normalize()  # 正規化以去除時間部分
# 判斷今天是否為月份至今的最後一個交易日
month_start = today.replace(day=1)
month_trading_days = close.loc[month_start:today]

# 檢查是否acc_position持倉陣列是空的，例如初始狀態，帳戶股票部位都是空的狀況
if not acc_position.position:
    order_executor = OrderExecutor(position_today, account=acc)
    order_executor.create_orders()  # 調整到這個持倉
    logging.info(f"今天是{today}，帳戶股票部位都是空的狀況，初始化持倉")
    logging.info(f"將於下一個交易調整持倉為{position_today.position}")


if not month_trading_days.empty:
    first_trading_day = month_trading_days.index[0]
    last_trading_day = month_trading_days.index[-1]
    if today == first_trading_day:
        logging.info(f"今天是{today}，為該月實際的第一個交易日，將執行換股調整")
        logging.info(f"將於下一個交易調整持倉為{position_today.position}")
        # 如果今天是該月實際的第一個交易日，則執行換股調整
        position_today = Position.from_report(report, fund, odd_lot=True)
        order_executor = OrderExecutor(position_today, account=acc)
        order_executor.create_orders()  # 調整到這個持倉

    elif today == last_trading_day:
        # 如果今天和close的最後一個交易日相同，則判斷帳戶股票部位是否有要提前出售的(跌8%)
        remove_ids = current_ids - new_ids
        if remove_ids:
            logging.info(f"今天是{today}，需要移除的股票有{remove_ids}，將於下一個交易日出售")
            # 為需要移除的股票設置數量為0，其它幾檔的數量維持不變
            for position in acc_position.position:
                if position['stock_id'] in remove_ids:
                    position['quantity'] = Decimal('0')

            order_executor = OrderExecutor(acc_position, account=acc)
            order_executor.create_orders()
        else:
            logging.info(f"今天是{today}，沒有跌停的股票需要出售，不需要調整持倉")
    else:
        logging.info(f"今天{today}是休市日")

else:
    logging.info(f"今天{today}是休市")


    




