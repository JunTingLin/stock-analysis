import os
import logging
import argparse
import datetime
from authentication import Authenticator
from config_loader import ConfigLoader
from line_notifier import LineNotifier
from portfolio_manager import PortfolioManager
from logger_config import LoggerConfig
from report_manager import ReportManager
from utils import is_trading_day

def initialize_environment(args):
    config_loader = ConfigLoader()
    config_loader.load_env_vars()
    config_loader.update_dynamic_params(args)

    auth = Authenticator()
    auth.login_finlab()
    acc = auth.login_fugle()

    return config_loader, acc

def setup_logger(current_datetime):
    log_directory = "logs"
    logger_config = LoggerConfig(log_directory, current_datetime)
    log_filepath = logger_config.setup_logging()

    return log_filepath

def execute_trading(config_loader, acc, current_datetime, log_filepath):
    if is_trading_day(acc) or True:
        portfolio_manager = PortfolioManager(
            acc, 
            config_loader.get("fund"), 
            config_loader.get("strategy_class_name"), 
            current_datetime, 
            config_loader.get("extra_bid_pct"),
            log_filepath
        )
        portfolio_manager.execute_order()

        report_finlab_directory = "output/report_finlab"
        report_final_directory = "output/report_final"
        report_template_path = "templates/report_template.html"

        data_dict = portfolio_manager.update_data_dict(report_finlab_directory)
        report_manager = ReportManager(data_dict, report_finlab_directory, report_final_directory, current_datetime, report_template_path)
        final_report_path = report_manager.save_final_report()

        # 獲取公開 URL 基礎地址
        public_base_url = config_loader.get("public_base_url")
        
        # 將本地報告路徑轉換為相對於公開基礎 URL 的路徑
        relative_report_path = os.path.relpath(final_report_path, start="output")
        public_report_url = f"{public_base_url}/{relative_report_path.replace(os.path.sep, '/')}"
        
        # 初始化 LineNotifier 並發送推播通知
        line_token = config_loader.get_env_var("LINE_NOTIFY_TOKEN")
        notifier = LineNotifier(line_token)
        notifier.send_notification(f"Report generated on {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}:\n {public_report_url}")

        
    else:
        logging.info("今天不是交易日，無需執行下單操作。")

def main():
    parser = argparse.ArgumentParser(description='Process parameters for order execution.')
    parser.add_argument('--extra_bid_pct', type=float, help='Extra bid percentage for order execution')
    args = parser.parse_args()

    config_loader, acc = initialize_environment(args)
    current_datetime = datetime.datetime.now()

    log_filepath = setup_logger(current_datetime)
    execute_trading(config_loader, acc, current_datetime, log_filepath)



if __name__ == "__main__":
    main()
