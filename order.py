import logging
import argparse
import datetime
from authentication import Authenticator
from config_loader import ConfigLoader
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
        
    else:
        logging.info("今天不是交易日，無需執行下單操作。")

def main():
    parser = argparse.ArgumentParser(description='Process parameters for order execution.')
    parser.add_argument('--extra_bid_pct', type=float, help='Extra bid percentage for order execution')
    args = parser.parse_args()

    config_loader, acc = initialize_environment(args)
    current_datetime = datetime.datetime.now()

    log_filepath = setup_logger(config_loader, current_datetime)
    execute_trading(config_loader, acc, current_datetime, log_filepath)



if __name__ == "__main__":
    main()
