import datetime
import logging
from logger_manager import LoggerManager
from authentication import Authenticator
from config_loader import ConfigLoader
from finlab.portfolio import Portfolio
from finlab.portfolio import PortfolioSyncManager

batch_timestamp = datetime.datetime.now()

log_config = LoggerManager(
    base_log_directory="logs",
    current_datetime=batch_timestamp,
    user_id="junting",
    broker="fugle"
)
log_file = log_config.setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"Log file: {log_file}")

userId = 'junting'
broker = 'fugle'
logger.info(f"userId: {userId}, broker: {broker}")

config_loader = ConfigLoader("config.yaml")
config_loader.load_global_env_vars()
config_loader.load_user_config(userId, broker)
auth = Authenticator()
auth.login_finlab()
account = auth.login_broker(broker)


def load_strategy(strategy_class_name):
    if strategy_class_name == 'TibetanMastiffTWStrategy':
        from strategy_class.tibetanmastiff_tw_strategy import TibetanMastiffTWStrategy as strategy_class
    elif strategy_class_name == 'PeterWuStrategy':
        from strategy_class.peterwu_tw_strategy import PeterWuStrategy as strategy_class
    else:
        raise ValueError(f"Unknown strategy class: {strategy_class_name}")
    return strategy_class()

strategy_class_name = config_loader.get_user_constant("strategy_class_name")
strategy = load_strategy(strategy_class_name)
report = strategy.run_strategy()

port = Portfolio({
    'strategy': (report, 1.0),
})
pm_name = f"{userId}_{broker}"
try:
    pm = PortfolioSyncManager.from_local(name=pm_name)
except FileNotFoundError:
    pm = PortfolioSyncManager()

total_balance = account.get_total_balance()
if total_balance <= 0:
    raise ValueError(f"{userId}'s total balance is not positive. Please check your {broker} account balance.")

rebalance_safety_weight = config_loader.get_user_constant("rebalance_safety_weight")
pm.update(port, total_balance=total_balance, rebalance_safety_weight=rebalance_safety_weight, odd_lot=True)
pm.to_local(name=pm_name)

extra_bid_pct = config_loader.get_user_constant("extra_bid_pct")
view_only = config_loader.get_user_constant("view_only")
pm.sync(account, extra_bid_pct=extra_bid_pct, view_only=view_only)


