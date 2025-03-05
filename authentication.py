import os
import sys
import logging
import traceback
import keyring
import finlab
from finlab.online.fugle_account import FugleAccount
from finlab.online.sinopac_account import SinopacAccount
from fugle_trade.util import setup_keyring
from config_loader import ConfigLoader

logger = logging.getLogger(__name__)

class Authenticator:

    def login_finlab(self):
        token = os.environ.get("FINLAB_API_TOKEN")
        if not token:
            raise EnvironmentError("Missing environment variable: FINLAB_API_TOKEN")
        
        finlab.login(token)
        logger.info("Successfully logged into FinLab")

    def _login_fugle(self):
        required_vars = [
            "FUGLE_CONFIG_PATH", 
            "FUGLE_MARKET_API_KEY", 
            "FUGLE_ACCOUNT", 
            "FUGLE_ACCOUNT_PASSWORD", 
            "FUGLE_CERT_PASSWORD"
        ]
        for var in required_vars:
            if not os.environ.get(var):
                raise EnvironmentError(f"Missing environment variable: {var}")

        # 根據作業系統判斷 cryptfile_pass.cfg 的位置
        if sys.platform.startswith("win"):
            cryptfile_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Python Keyring", "cryptfile_pass.cfg")
        elif sys.platform.startswith("linux"):
            cryptfile_path = os.path.join(os.path.expanduser("~"), ".local", "share", "python_keyring", "cryptfile_pass.cfg")
        else:
            raise EnvironmentError("Unsupported operating system for cryptfile_pass.cfg handling")

        # 如果檔案存在，先刪除
        if os.path.exists(cryptfile_path):
            try:
                os.remove(cryptfile_path)
                logger.info(f"Removed existing cryptfile_pass.cfg at {cryptfile_path}")
            except Exception as e:
                logger.error(f"Failed to remove cryptfile_pass.cfg at {cryptfile_path}: {e}")
                raise

        setup_keyring(os.environ["FUGLE_ACCOUNT"])
        keyring.set_password("fugle_trade_sdk:account", os.environ["FUGLE_ACCOUNT"], os.environ["FUGLE_ACCOUNT_PASSWORD"])
        keyring.set_password("fugle_trade_sdk:cert", os.environ["FUGLE_ACCOUNT"], os.environ["FUGLE_CERT_PASSWORD"])

        account = FugleAccount()
        logger.info("Successfully logged into Fugle")
        return account

    def _login_shioaji(self):
        required_vars = [
            "SHIOAJI_API_KEY", 
            "SHIOAJI_SECRET_KEY", 
            "SHIOAJI_CERT_PERSON_ID", 
            "SHIOAJI_CERT_PATH", 
            "SHIOAJI_CERT_PASSWORD"
        ]
        for var in required_vars:
            if not os.environ.get(var):
                raise EnvironmentError(f"Missing environment variable: {var}")

        account = SinopacAccount()
        logger.info("Successfully logged into Shioaji")
        return account

    def login_broker(self, broker: str):
        broker = broker.lower()
        if broker == "fugle":
            return self._login_fugle()
        elif broker == "shioaji":
            return self._login_shioaji()
        else:
            raise ValueError(f"Unsupported broker: {broker}")

if __name__ == "__main__":
    try:
        userId = 'junting'
        broker = 'fugle'
        config_loader = ConfigLoader("config.yaml")
        config_loader.load_global_env_vars()
        config_loader.load_user_config(userId, broker)
        auth = Authenticator()
        auth.login_finlab()
        account = auth.login_broker(broker)
        
        print("Account:", account)

    except Exception as e:
        traceback.print_exc()
