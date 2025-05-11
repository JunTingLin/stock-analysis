import argparse
import datetime
import logging
import os
from utils.logger_manager import LoggerManager
from utils.authentication import Authenticator
from utils.config_loader import ConfigLoader
from finlab.portfolio import Portfolio, PortfolioSyncManager
from dao import OrderDAO, AccountDAO
from utils.stock_mapper import StockMapper

logger = logging.getLogger(__name__)

class OrderExecutor:
    def __init__(self, user_name, broker_name, extra_bid_pct, view_only, config_path="config.yaml", base_log_directory="logs"):
        self.user_name = user_name
        self.broker_name = broker_name
        self.extra_bid_pct = extra_bid_pct
        self.view_only = view_only

        self.config_loader = ConfigLoader(config_path)
        self.config_loader.load_global_env_vars()
        self.config_loader.load_user_config(user_name, broker_name)

        self.auth = Authenticator()
        self.auth.login_finlab()
        self.account = self.auth.login_broker(broker_name)

        self.order_timestamp = datetime.datetime.now()
        self.logger_manager = LoggerManager(
            base_log_directory=base_log_directory,
            current_datetime=self.order_timestamp
        )
        self.log_file = self.logger_manager.setup_logging()
        logger.info(f"user_name: {self.user_name}, broker_name: {self.broker_name}")

        self.order_dao = OrderDAO()
        self.account_dao = AccountDAO()
        self.stock_mapper = StockMapper()

    def run_strategy_and_sync(self):
        strategy_class_name = self.config_loader.get_user_constant("strategy_class_name")
        strategy = self.load_strategy(strategy_class_name)
        report = strategy.run_strategy()

        port = Portfolio({
            'strategy': (report, 1.0),
        })
        pm_name = f"{self.user_name}_{self.broker_name}"
        try:
            pm = PortfolioSyncManager.from_local(name=pm_name)
        except FileNotFoundError:
            pm = PortfolioSyncManager()

        total_balance = self.account.get_total_balance()
        logger.info(f"Total balance: {total_balance}")
        if total_balance <= 0:
            raise ValueError(f"{self.user_name}'s total balance is not positive. Please check your {self.broker_name} account balance.")

        safety_weight = self.config_loader.get_user_constant("rebalance_safety_weight")
        pm.update(port, total_balance=total_balance, rebalance_safety_weight=safety_weight, odd_lot=True)
        # pm.update(port, total_balance=total_balance, rebalance_safety_weight=safety_weight, odd_lot=True, force_override_difference=True, smooth_transition=False)
        pm.to_local(name=pm_name)

        pm.sync(self.account, extra_bid_pct=self.extra_bid_pct, view_only=self.view_only)
        logger.info("Portfolio synced")

        order_logs = self.logger_manager.extract_order_logs(self.log_file)

        if not order_logs:
            logger.warning("Today not have any order")
            return
        else:

            for order in order_logs:
                order['stock_name'] = self.stock_mapper.map(order['stock_id'])

            account_name = self.user_name+"_"+self.broker_name
            account_id = self.account_dao.get_account_id(account_name, broker_name=self.broker_name, user_name=self.user_name)
            self.order_dao.insert_order_logs(order_logs, account_id, self.order_timestamp, view_only=self.view_only)
        

    def load_strategy(self, strategy_class_name):
        if strategy_class_name == 'TibetanMastiffTWStrategy':
            from strategy_class.tibetanmastiff_tw_strategy import TibetanMastiffTWStrategy as strategy_class
        elif strategy_class_name == 'PeterWuStrategy':
            from strategy_class.peterwu_tw_strategy import PeterWuStrategy as strategy_class
        elif strategy_class_name == 'AllenChuangBasicTWStrategy':
            from strategy_class.alan_tw_strategy_1 import AlanTwStrategy1 as strategy_class
        elif strategy_class_name == 'RAndDManagementStrategy':
            from strategy_class.r_and_d_management_strategy import RAndDManagementStrategy as strategy_class
        else:
            raise ValueError(f"Unknown strategy class: {strategy_class_name}")
        return strategy_class()

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    parser = argparse.ArgumentParser(description="Run OrderExecutor")
    parser.add_argument("--user_name", required=True, help="User name (e.g., junting)")
    parser.add_argument("--broker_name", required=True, help="Broker name (e.g., fugle)")
    parser.add_argument("--extra_bid_pct", type=float, default=0.0,
                        help="Extra bid percentage (e.g., 0.01)")
    parser.add_argument("--view_only", action='store_true', help="Run in view-only mode")

    args = parser.parse_args()
    logger.info(f"args: {args}")

    try:
        order_executor = OrderExecutor(
            user_name=args.user_name,
            broker_name=args.broker_name,
            extra_bid_pct=args.extra_bid_pct,
            view_only=args.view_only,
            config_path = os.path.join(root_dir, "config.yaml"),
            base_log_directory = os.path.join(root_dir, "logs")
        )
        order_executor.run_strategy_and_sync()
    except Exception as e:
        logger.exception(e)

    # python -m jobs.order_executor --user_name junting --broker_name fugle --extra_bid_pct 0 --view_only
    # python -m jobs.order_executor --user_name junting --broker_name shioaji --extra_bid_pct 0 --view_only
    # python -m jobs.order_executor --user_name alan --broker_name shioaji --extra_bid_pct 0 --view_only
