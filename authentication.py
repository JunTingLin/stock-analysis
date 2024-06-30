import os
import logging
import platform
import traceback

import keyring
import finlab
from finlab.online.fugle_account import FugleAccount
from fugle_trade.util import setup_keyring

def check_env_vars():
    # 檢查環境變數是否已經設置
    required_vars = [
        'FINLAB_API_TOKEN', 'FUGLE_CONFIG_PATH', 'FUGLE_MARKET_API_KEY',
        'FUGLE_ACCOUNT', 'FUGLE_ACCOUNT_PASSWORD', 'FUGLE_CERT_PASSWORD',
        'PYTHON_KEYRING_BACKEND', 'FUND', 'STRATEGY_CLASS', 'FLASK_SERVER_PORT'
    ]
    
    env_vars_set = all(var in os.environ for var in required_vars)

    if not env_vars_set:
        logging.info("Environment variables not set. Setting up...")
        # 判斷作業系統並設置環境變數
        if platform.system() == "Windows":
            from config.env_setup import env_setup_for_windows
            env_setup_for_windows()
        else:
            from config.env_setup import env_setup_for_linux
            env_setup_for_linux()

def login_finlab():
    finlab.login(os.environ["FINLAB_API_TOKEN"])
    logging.info("Logged into FinLab.")

def login_fugle():
    # ~/.local/share/python_keyring/cryptfile_pass.cfg
    setup_keyring(os.environ["FUGLE_ACCOUNT"])
    keyring.set_password("fugle_trade_sdk:account", os.environ["FUGLE_ACCOUNT"], os.environ["FUGLE_ACCOUNT_PASSWORD"])
    keyring.set_password("fugle_trade_sdk:cert", os.environ["FUGLE_ACCOUNT"], os.environ["FUGLE_CERT_PASSWORD"])

    acc = FugleAccount()
    logging.info("Logged into Fugle.")
    return acc


if __name__ == "__main__":
    try:
        check_env_vars()
        login_finlab()
        acc = login_fugle()
        print(acc)
    except Exception as e:
        # print(e)
        traceback.print_exc()
