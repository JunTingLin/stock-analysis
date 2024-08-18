import argparse
from logger_config import setup_logging
import logging
import os


from authentication import check_env_vars, login_finlab, login_fugle
from model.trading_info import TradingInfo
from notifier import notify_users
from portfolio_management import get_current_portfolio_info, get_next_portfolio_info,  get_order_execution_info
from finlab.online.order_executor import Position, OrderExecutor
from utils import read_warnings_from_log, get_current_formatted_datetime, is_trading_day
from portfolio_rebalancer import rebalance_portfolio

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



def main(fund, strategy_class_name, flask_server_port, extra_bid_pct):
    log_filepath = setup_logging()
    check_env_vars()
    login_finlab()

    strategy = load_strategy(strategy_class_name)
    report = strategy.run_strategy()

    acc = login_fugle()
    config_file_name = os.path.basename(os.environ['FUGLE_CONFIG_PATH'])

    position_acc = acc.get_position()
    
    # 判斷今日是否為交易日
    if is_trading_day(acc):
        position_today = Position.from_report(report, fund, odd_lot=True)
        position_today = rebalance_portfolio(position_today, position_acc)

        if position_today is not None:
            order_executor = OrderExecutor(position_today, account=acc)
            order_executor.create_orders(extra_bid_pct=extra_bid_pct)

    





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process parameters for order execution.')
    parser.add_argument('--fund', type=int, required=True, help='Fund amount')
    parser.add_argument('--strategy_class', type=str, required=True, help='Strategy class name')
    parser.add_argument('--flask_server_port', type=int, required=True, help='Flask server port')
    parser.add_argument('--extra_bid_pct', type=float, default=0, help='Extra bid percentage for order execution')

    args = parser.parse_args()
    main(args.fund, args.strategy_class, args.flask_server_port, args.extra_bid_pct)
    
    # main(fund = 80000,
    #     strategy_class_name = 'TibetanMastiffTWStrategy',
    #     flask_server_port = 5000,
    #     extra_bid_pct = 0
    # )
