import argparse
from logger_config import setup_logging
import logging
import os
from decimal import Decimal

from authentication import check_env_vars, login_finlab, login_fugle
from model.trading_info import TradingInfo
from notifier import notify_users
from portfolio_management import get_current_portfolio_info, get_next_portfolio_info,  get_order_execution_info
from finlab.online.order_executor import Position, OrderExecutor
from utils import get_current_formatted_datetime, read_warnings_from_log

def load_strategy(strategy_class_name):
    if strategy_class_name == 'TibetanMastiffTWStrategy':
        from strategy_class.tibetanmastiff_tw_strategy import TibetanMastiffTWStrategy as strategy_class
    elif strategy_class_name == 'PeterWuStrategy':
        from strategy_class.peterwu_tw_strategy import PeterWuStrategy as strategy_class
    else:
        raise ValueError(f"Unknown strategy class: {strategy_class_name}")
    return strategy_class()

def set_trading_info(trading_info, attr_dict):
    for key, value in attr_dict.items():
        trading_info.set_attribute(key, value)

def execute_trades(position_today, acc, extra_bid_pct, trading_info, company_basic_info, log_filepath):
    new_ids = set(p['stock_id'] for p in position_today.position)
    current_ids = set(p['stock_id'] for p in acc.get_position().position)
    add_ids = new_ids - current_ids
    remove_ids = current_ids - new_ids

    if add_ids:
        try:
            order_executor = OrderExecutor(position_today, account=acc)
            order_executor.create_orders(extra_bid_pct=extra_bid_pct)
            portfolio_details = get_next_portfolio_info(position_today.position, company_basic_info)
            set_trading_info(trading_info, {'positions_next': portfolio_details})
            logging.info(f"將於下一個交易調整持倉為: {portfolio_details}")
            warning_logs = read_warnings_from_log(log_filepath)
            order_details = get_order_execution_info(warning_logs, company_basic_info)
            set_trading_info(trading_info, {'order_details': order_details})
        except Exception as e:
            logging.error(f"調整持倉失敗: {e}")

    elif remove_ids:
        for position in acc.get_position().position:
            if position['stock_id'] in remove_ids:
                position['quantity'] = Decimal('0')
        try:
            order_executor = OrderExecutor(acc.get_position(), account=acc)
            order_executor.create_orders(extra_bid_pct=extra_bid_pct)
            portfolio_details = get_next_portfolio_info(position_today.position, company_basic_info)
            set_trading_info(trading_info, {'positions_next': portfolio_details})
            logging.info(f"將於下一個交易調整持倉為{portfolio_details}")
            warning_logs = read_warnings_from_log(log_filepath)
            order_details = get_order_execution_info(warning_logs, company_basic_info)
            set_trading_info(trading_info, {'order_details': order_details})
        except Exception as e:
            logging.error(f"調整持倉失敗: {e}")
    else:
        logging.info("持倉無需變化")

def main(fund, strategy_class_name, flask_server_port, extra_bid_pct):
    log_filepath = setup_logging()
    check_env_vars()
    login_finlab()

    strategy = load_strategy(strategy_class_name)
    report = strategy.run_strategy()
    close = strategy.get_close_prices()
    company_basic_info = strategy.get_company_basic_info()

    trading_info = TradingInfo()
    acc = login_fugle()
    config_file_name = os.path.basename(os.environ['FUGLE_CONFIG_PATH'])

    position_acc = acc.get_position()
    stock_value, portfolio_details = get_current_portfolio_info(position_acc.position, close, company_basic_info)
    set_trading_info(trading_info, {
        'is_simulation': True if config_file_name == 'config.simulation.ini' else False,
        'bank_cash_acc': acc.get_cash(),
        'positions_acc': portfolio_details,
        'positions_cash_acc': stock_value,
        'total_cash': acc.get_cash() + stock_value,
        'fund': fund,
        'today': get_current_formatted_datetime()
    })

    position_today = Position.from_report(report, fund, odd_lot=True)
    execute_trades(position_today, acc, extra_bid_pct, trading_info, company_basic_info, log_filepath)

    logging.info(trading_info.data)

    notify_users(flask_server_port, config_file_name, trading_info)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process parameters for order execution.')
    parser.add_argument('--fund', type=int, required=True, help='Fund amount')
    parser.add_argument('--strategy_class', type=str, required=True, help='Strategy class name')
    parser.add_argument('--flask_server_port', type=int, required=True, help='Flask server port')
    parser.add_argument('--extra_bid_pct', type=float, default=0, help='Extra bid percentage for order execution')
    # args = parser.parse_args()

    # main(args.fund, args.strategy_class, args.flask_server_port, args.extra_bid_pct)
    main(fund = 80000,
        strategy_class_name = 'TibetanMastiffTWStrategy',
        flask_server_port = 5000,
        extra_bid_pct = 0
    )
