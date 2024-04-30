from TibetanMastiff_TW_Strategy import TibetanMastiffTWStrategy
from finlab.online.fugle_account import FugleAccount
from finlab.online.order_executor import OrderExecutor, Position
import finlab
import os
import configparser
import pandas as pd
from decimal import Decimal
import logger_config
import logging

from models.line_message import LineMessage
from services.message_service import MessageService
from services.notification_service import NotificationService

# 設置日誌
logger_config.setup_logging()

# 讀取設定檔
config = configparser.ConfigParser()
config_file_name = 'config.simulation.ini'
config_file_path = os.path.join('config', config_file_name)
config.read(config_file_path)

# 登入FinLab
finlab.login(config['FinLab']['API_TOKEN'])

# 登入玉山富果
os.environ['FUGLE_CONFIG_PATH'] = config_file_path
os.environ['FUGLE_MARKET_API_KEY'] = config['FUGLE_MARKET']['API_KEY']
acc = FugleAccount()

# 初始化策略
strategy = TibetanMastiffTWStrategy()
report = strategy.run_strategy()
close = strategy.get_close_prices()

line_msg = LineMessage()

today = pd.Timestamp.now().normalize()
line_msg.set_date(today.date())

if today == close.index[-1]:
    # 執行交易邏輯
    fund = 100000 * 0.8  # acc.get_cash()
    logging.info(f"當前帳戶目前資金為: NT${acc.get_cash()}")
    line_msg.set_cash(acc.get_cash())

    # 帳戶持倉
    position_acc = acc.get_position()
    logging.info(f"當前帳戶目前持倉為: {position_acc.position}")
    line_msg.set_positions_acc(position_acc.position)
    current_ids = set(p['stock_id'] for p in position_acc.position)

    # 獲取由report物件生成的今日持倉
    position_today = Position.from_report(report, fund, odd_lot=True)
    new_ids = set(p['stock_id'] for p in position_today.position)

    # 初始狀態，帳戶股票部位都是空的狀況
    if not position_acc.position:
        order_executor = OrderExecutor(position_today, account=acc)
        order_executor.create_orders()  # 調整到這個持倉
        logging.info(f"帳戶股票部位都是空的狀況，初始化持倉")
        line_msg.set_message(f"帳戶股票部位都是空的狀況，初始化持倉")
        logging.info(f"將於下一個交易調整持倉為: {position_today.position}")
        line_msg.set_positions_next(position_today.position)

    else:
        # 檢查今天是否為月初第一天，月初第一天確定換股調整
        month_start = today.replace(day=1)
        month_trading_days = close.loc[month_start:today]

        first_trading_day = month_trading_days.index[0]
        last_trading_day = month_trading_days.index[-1]
        if today == first_trading_day:
            logging.info(f"為該月實際的第一個交易日，將執行換股調整")
            line_msg.set_message(f"為該月實際的第一個交易日，將執行換股調整")
            logging.info(f"將於下一個交易調整持倉為{position_today.position}")
            line_msg.set_positions_next(position_today.position)
            # 如果今天是該月實際的第一個交易日，則執行換股調整
            position_today = Position.from_report(report, fund, odd_lot=True)
            order_executor = OrderExecutor(position_today, account=acc)
            order_executor.create_orders()  # 調整到這個持倉

        elif today == last_trading_day:
            # 如果今天和close的最後一個交易日相同，則判斷帳戶股票部位是否有要提前出售的(跌8%)
            remove_ids = current_ids - new_ids
            if remove_ids:
                # 為需要移除的股票設置數量為0，其它幾檔的數量維持不變
                for position in position_acc.position:
                    if position['stock_id'] in remove_ids:
                        position['quantity'] = Decimal('0')
                
                logging.info(f"需要移除的股票有{remove_ids}，將於下一個交易日出售")
                line_msg.set_message(f"需要移除的股票有{remove_ids}，將於下一個交易日出售")
                logging.info(f"將於下一個交易調整持倉為{position_acc.position}")

                order_executor = OrderExecutor(position_acc, account=acc)
                order_executor.create_orders()
            else:
                logging.info(f"沒有跌停的股票需要出售，不需要調整持倉")
                line_msg.set_message(f"沒有跌停的股票需要出售，不需要調整持倉")

else:
    logging.info(f"今天是休市日喔")
    line_msg.set_message(f"今天是休市日喔")





message_service = MessageService()
formatted_message = message_service.render_message(line_msg.to_dict())
print(formatted_message)

notification_service = NotificationService()
notification_service.send_notification(formatted_message)
