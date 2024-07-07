import logger_config
import logging
import os
import pandas as pd
from decimal import Decimal

from authentication import check_env_vars, login_finlab, login_fugle
from model.trading_info import TradingInfo
from notifier import notify_users
from portfolio_management import calculate_portfolio_value
from finlab.online.order_executor import Position, OrderExecutor


# 設置日誌
logger_config.setup_logging()

# 檢查環境變數
check_env_vars()

# 登入FinLab
login_finlab()

# 從環境變量中獲取 FUND 和策略
FUND = int(os.getenv('FUND'))
STRATEGY_CLASS = os.getenv('STRATEGY_CLASS')

# 根據 STRATEGY_CLASS 動態導入策略類
if STRATEGY_CLASS == 'TibetanMastiffTWStrategy':
    from strategy_class.tibetanmastiff_tw_strategy import TibetanMastiffTWStrategy as strategy_class
elif STRATEGY_CLASS == 'PeterWuStrategy':
    from strategy_class.peterwu_tw_strategy import PeterWuStrategy as strategy_class
else:
    raise ValueError(f"Unknown strategy class: {STRATEGY_CLASS}")

# 初始化策略
strategy = strategy_class()
report = strategy.run_strategy()
close = strategy.get_close_prices()
company_basic_info = strategy.get_company_basic_info()

# 初始化交易資訊物件
trading_info = TradingInfo()

# 登入Fugle
acc = login_fugle()
config_file_name = os.path.basename(os.environ['FUGLE_CONFIG_PATH'])
trading_info.set_attribute('is_simulation', True if config_file_name == 'config.simulation.ini' else False)
cash = acc.get_cash()
trading_info.set_attribute('bank_cash_acc', cash)
position_acc = acc.get_position()
stock_value, portfolio_details = calculate_portfolio_value(position_acc.position, close, company_basic_info)
trading_info.set_attribute('positions_acc', portfolio_details)
trading_info.set_attribute('positions_cash_acc', stock_value)
total_cash = cash + stock_value
trading_info.set_attribute('total_cash', total_cash)

trading_info.set_attribute('fund', FUND)

today = pd.Timestamp.now().normalize()
trading_info.set_attribute('today', str(today.date()))

force_trading_day = False  # 是否強制今天為交易日，用於debug

# 判斷今日是否為交易日
if today != close.index[-1] and not force_trading_day:
    trading_info.set_attribute('is_trading_day', False)
    logging.info(f"今天{today}不為交易日")
else:
    trading_info.set_attribute('is_trading_day', True)
    logging.info(f"今天{today}為交易日")

    # 執行交易邏輯
    position_today = Position.from_report(report, FUND, odd_lot=True)
    new_ids = set(p['stock_id'] for p in position_today.position)
    current_ids = set(p['stock_id'] for p in position_acc.position)
    add_ids = new_ids - current_ids
    remove_ids = current_ids - new_ids

    if add_ids != set():
        try:
            order_executor = OrderExecutor(position_today, account=acc)
            order_executor.create_orders()  # 調整到這個持倉
            _, portfolio_details = calculate_portfolio_value(position_today.position, close, company_basic_info)
            trading_info.set_attribute('positions_next', portfolio_details)
            logging.info(f"將於下一個交易調整持倉為: {portfolio_details}")
        except Exception as e:
            logging.error(f"調整持倉失敗: {e}")

    elif remove_ids != set():
        for position in position_acc.position:
            if position['stock_id'] in remove_ids:
                position['quantity'] = Decimal('0')

        try:
            order_executor = OrderExecutor(position_acc, account=acc)
            order_executor.create_orders()
            _, portfolio_details = calculate_portfolio_value(position_acc.position, close, company_basic_info)
            trading_info.set_attribute('positions_next', portfolio_details)
            logging.info(f"需要移除的股票有{remove_ids}，將於下一個交易日出售")
            logging.info(f"將於下一個交易調整持倉為{portfolio_details}")
        except Exception as e:
            logging.error(f"提前出售失敗: {e}")

    else:
        logging.info("持倉無需變化")

    logging.info(trading_info.data)


# 使用 notify_users 函數
notify_users(config_file_name, trading_info)