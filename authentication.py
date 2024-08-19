import os
import logging
import traceback
import keyring
import finlab
from finlab.online.fugle_account import FugleAccount
from fugle_trade.util import setup_keyring
from config_loader import ConfigLoader

class Authenticator:
    def __init__(self):
        self.check_env_vars()

    def check_env_vars(self):
        required_vars = [
            'FINLAB_API_TOKEN', 'FUGLE_CONFIG_PATH', 'FUGLE_MARKET_API_KEY',
            'FUGLE_ACCOUNT', 'FUGLE_ACCOUNT_PASSWORD', 'FUGLE_CERT_PASSWORD',
            'PYTHON_KEYRING_BACKEND'
        ]
        
        for var in required_vars:
            if var not in os.environ:
                raise EnvironmentError(f"Missing required environment variable: {var}")
        logging.info("Environment variables are set.")

    def login_finlab(self):
        finlab.login(os.environ["FINLAB_API_TOKEN"])
        logging.info("Logged into FinLab.")

    def login_fugle(self):
        # ~/.local/share/python_keyring/cryptfile_pass.cfg
        # C:\Users\<YourUsername>\AppData\Local\Python Keyring\cryptfile_pass.cfg
        setup_keyring(os.environ["FUGLE_ACCOUNT"])
        keyring.set_password("fugle_trade_sdk:account", os.environ["FUGLE_ACCOUNT"], os.environ["FUGLE_ACCOUNT_PASSWORD"])
        keyring.set_password("fugle_trade_sdk:cert", os.environ["FUGLE_ACCOUNT"], os.environ["FUGLE_CERT_PASSWORD"])

        acc = FugleAccount()
        logging.info("Logged into Fugle.")
        return acc


if __name__ == "__main__":
    try:
        config_loader = ConfigLoader()
        config_loader.load_env_vars()
        auth = Authenticator()
        auth.login_finlab()
        acc = auth.login_fugle()
        print(acc)
    except Exception as e:
        # print(e)
        traceback.print_exc()
