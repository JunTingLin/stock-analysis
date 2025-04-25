import argparse
import logging
import os
from utils.config_loader import ConfigLoader
from utils.logger_manager import LoggerManager
from datetime import datetime

logger = logging.getLogger(__name__)

class BacktestExecutor:
    def __init__(self, strategy_class_name, config_path="config.yaml", base_log_directory="logs"):
        self.strategy_class_name = strategy_class_name
        self.backtest_timestamp = datetime.now()
        self.logger_manager = LoggerManager(
            base_log_directory=base_log_directory,
            current_datetime=self.backtest_timestamp,
        )
        self.config_loader = ConfigLoader(config_path)
        self.config_loader.load_global_env_vars()
        self.log_file = self.logger_manager.setup_logging()

    def run_strategy_and_save(self):
        strategy = self.load_strategy()
        report = strategy.run_strategy()
        self.save_finlab_report(report)


    def save_finlab_report(self, report, base_directory="assets/"):
        subdirectory = self.strategy_class_name
        report_directory = os.path.join(base_directory, subdirectory)
        if not os.path.exists(report_directory):
            os.makedirs(report_directory)
        datetime_str = self.backtest_timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        save_report_path = os.path.join(report_directory, f"{datetime_str}.html")
        report.display(save_report_path=save_report_path)
        


    def load_strategy(self):
        if self.strategy_class_name == 'TibetanMastiffTWStrategy':
            from strategy_class.tibetanmastiff_tw_strategy import TibetanMastiffTWStrategy as strategy_class
        elif self.strategy_class_name == 'PeterWuStrategy':
            from strategy_class.peterwu_tw_strategy import PeterWuStrategy as strategy_class
        elif self.strategy_class_name == 'AlanTwStrategy1':
            from strategy_class.alan_tw_strategy_1 import AlanTwStrategy1 as strategy_class
        else:
            raise ValueError(f"Unknown strategy class: {self.strategy_class_name}")
        return strategy_class()

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    parser = argparse.ArgumentParser(description="Run BacktestExecutor")
    parser.add_argument("--strategy_class_name", required=True, help="strategy_class_name (e.g., TibetanMastiffTWStrategy)")

    args = parser.parse_args()
    logger.info(f"args: {args}")

    try:
        backtest_executor = BacktestExecutor(strategy_class_name=args.strategy_class_name)
        backtest_executor.run_strategy_and_save()
    except Exception as e:
        logger.exception(e)

    # python -m jobs.backtest_executor --strategy_class_name TibetanMastiffTWStrategy
