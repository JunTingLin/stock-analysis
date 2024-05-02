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

# 執行交易邏輯
fund = acc.get_cash() * 0.8
print(f"當前帳戶目前資金為: NT${acc.get_cash()}")

# 帳戶持倉
position_acc = acc.get_position()
print(f"當前帳戶目前持倉為: {position_acc.position}")

# 獲取由report物件生成的今日持倉
position_today = Position.from_report(report, fund, odd_lot=True)

order_executor = OrderExecutor(position_today, account=acc)
order_executor.create_orders()  # 調整到這個持倉

