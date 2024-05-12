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

line_msg = LineMessage()

try: 
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

    today = pd.Timestamp.now().normalize()
    line_msg.set_date(today.date())

    # 執行交易邏輯
    fund = acc.get_cash() * 0.8
    logging.info(f"當前帳戶目前資金為: NT${acc.get_cash()}")
    line_msg.set_cash(acc.get_cash())

    # 帳戶持倉
    position_acc = acc.get_position()
    logging.info(f"當前帳戶目前持倉為: {position_acc.position}")
    line_msg.set_positions_acc(position_acc.position)
    current_ids = set(p['stock_id'] for p in position_acc.position)

    if today == close.index[-1]:
        # 獲取由report物件生成的今日持倉
        position_today = Position.from_report(report, fund, odd_lot=True)
        new_ids = set(p['stock_id'] for p in position_today.position)

        # 初始狀態，帳戶股票部位都是空的狀況
        if not position_acc.position:
            try:
                order_executor = OrderExecutor(position_today, account=acc)
                order_executor.create_orders()  # 調整到這個持倉
                logging.info(f"帳戶股票部位都是空的狀況，初始化持倉")
                line_msg.append_message(f"帳戶股票部位都是空的狀況，初始化持倉")
                logging.info(f"將於下一個交易調整持倉為: {position_today.position}")
                line_msg.set_positions_next(position_today.position)
            except Exception as e:
                logging.error(f"初始化持倉失敗: {e}")
                line_msg.append_error(f"初始化持倉失敗: {e}")

        else:
            add_ids = new_ids - current_ids
            remove_ids = current_ids - new_ids
            if add_ids != set():
                try:
                    order_executor = OrderExecutor(position_today, account=acc)
                    order_executor.create_orders()  # 調整到這個持倉
                    logging.info(f"持倉有變化，將於下一個交易調整持倉")
                    line_msg.append_message(f"持倉有變化，將於下一個交易調整持倉")
                    logging.info(f"將於下一個交易調整持倉為: {position_today.position}")
                    line_msg.set_positions_next(position_today.position)
                except Exception as e:
                    logging.error(f"調整持倉失敗: {e}")
                    line_msg.append_error(f"調整持倉失敗: {e}")
            elif remove_ids:
                # 為需要移除的股票設置數量為0，其它幾檔的數量維持不變
                for position in position_acc.position:
                    if position['stock_id'] in remove_ids:
                        position['quantity'] = Decimal('0')
                try:
                    order_executor = OrderExecutor(position_acc, account=acc)
                    order_executor.create_orders()
                    logging.info(f"需要移除的股票有{remove_ids}，將於下一個交易日出售")
                    line_msg.append_message(f"需要移除的股票有{remove_ids}，將於下一個交易日出售")
                    logging.info(f"將於下一個交易調整持倉為{position_acc.position}")
                    line_msg.set_positions_next(position_acc.position)
                except Exception as e:
                    logging.error(f"提前出售失敗: {e}")
                    line_msg.append_error(f"提前出售失敗: {e}")
            else:
                logging.info(f"不需要調整持倉")
                line_msg.append_message(f"不需要調整持倉")

    else:
        logging.info(f"今天是休市日喔")
        line_msg.append_message(f"今天是休市日喔")

except Exception as e:
    logging.error(f"發生錯誤: {e}")
    line_msg.append_error(f"發生錯誤: {e}")





message_service = MessageService()
formatted_message = message_service.render_message(line_msg.to_dict())
print(formatted_message)

notification_service = NotificationService()
if config_file_name == 'config.ini':
    notification_service.send_notification_to_all_users(formatted_message)
else:
    notification_service.send_notification_to_developer(formatted_message)
