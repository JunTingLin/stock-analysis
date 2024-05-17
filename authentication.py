import os
import logging
import platform
import traceback

import keyring
import finlab
from finlab.online.fugle_account import FugleAccount
from fugle_trade.util import setup_keyring
from config.env_setup import env_setup_for_windows



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

def login_all():
    # 判斷作業系統
    if platform.system() == "Windows":
        # 設置 Windows 環境變數
        env_setup_for_windows()
    else:
        # Linux 下可以直接使用環境變量，什麼都不用做
        pass
    login_finlab()
    acc = login_fugle()
    return acc

if __name__ == "__main__":
    try:
        acc = login_all()
        print(acc)
    except Exception as e:
        print(e)
        traceback.print_exc()
