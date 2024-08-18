import logging
import argparse
import datetime
from portfolio_manager import PortfolioManager
from authentication import login_finlab, login_fugle, check_env_vars
from logger_config import setup_logging
from utils import is_trading_day

def main(fund, strategy_class_name, extra_bid_pct, flask_server_port):
    log_filepath = setup_logging()  # 初始化日誌記錄
    check_env_vars()  # 檢查環境變量
    login_finlab()  # 登錄FinLab

    acc = login_fugle()  # 登錄Fugle
    current_datetime = datetime.datetime.now()  # 獲取當前的日期時間

    # 判斷今天是否為交易日
    if is_trading_day(acc) or True:
        # 創建 PortfolioManager 的實例
        portfolio_manager = PortfolioManager(acc, fund, strategy_class_name, current_datetime, extra_bid_pct)

        # 執行下單流程並獲取 data_dict
        data_dict = portfolio_manager.execute_order()

        # 對 data_dict 進行後續處理
        print(data_dict)
        # 其他後續處理...
    else:
        logging.info("今天不是交易日，無需執行下單操作。")




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
