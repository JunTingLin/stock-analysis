from authentication import Authenticator
from config_loader import ConfigLoader
from finlab.online.order_executor import OrderExecutor


config_loader = ConfigLoader()
config_loader.load_env_vars()

auth = Authenticator()
auth.login_finlab()
acc = auth._login_fugle()

order_executor = OrderExecutor(None, acc)
order_executor.cancel_orders()
print("cancel orders successfully")
