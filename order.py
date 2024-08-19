import logging
import argparse
import datetime
from portfolio_manager import PortfolioManager
from authentication import login_finlab, login_fugle, check_env_vars
from logger_config import setup_logging
from utils import is_trading_day

def main(fund, strategy_class_name, extra_bid_pct, flask_server_port):
    pkl_paths = {
        'financial_summary': 'data/financial_summary.pkl'
    }
    log_filepath = setup_logging()
    check_env_vars()
    login_finlab()

    acc = login_fugle()
    current_datetime = datetime.datetime.now()

    if is_trading_day(acc):
        portfolio_manager = PortfolioManager(acc, fund, strategy_class_name, current_datetime, extra_bid_pct)
        portfolio_manager.execute_order()
        data_dict = portfolio_manager.update_data_dict(pkl_paths)

        print(data_dict)

    else:
        logging.info("今天不是交易日，無需執行下單操作。")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process parameters for order execution.')
    parser.add_argument('--fund', type=int, required=True, help='Fund amount')
    parser.add_argument('--strategy_class', type=str, required=True, help='Strategy class name')
    parser.add_argument('--flask_server_port', type=int, required=True, help='Flask server port')
    parser.add_argument('--', type=float, default=0, help='Extra bid percentage for order execution')

    # args = parser.parse_args()
    # main(args.fund, args.strategy_class, args.flask_server_port, args.extra_bid_pct)
    
    main(fund = 80000,
        strategy_class_name = 'TibetanMastiffTWStrategy',
        flask_server_port = 5000,
        extra_bid_pct = 0
    )
