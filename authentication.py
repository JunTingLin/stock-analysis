import os
import logging
import keyring
import finlab
from finlab.online.fugle_account import FugleAccount
from fugle_trade.util import setup_keyring
from config.env_setup import env_setup



def login_finlab():
    finlab.login(os.environ["FINLAB_API_TOKEN"])
    logging.info("Logged into FinLab.")

def login_fugle():
    setup_keyring('os.environ["FUGLE_ACCOUNT"]')
    keyring.set_password("fugle_trade_sdk:account", os.environ["FUGLE_ACCOUNT"], os.environ["FUGLE_ACCOUNT_PASSWORD"])
    keyring.set_password("fugle_trade_sdk:cert", os.environ["FUGLE_ACCOUNT"], os.environ["FUGLE_CERT_PASSWORD"])

    acc = FugleAccount()
    logging.info("Logged into Fugle.")
    return acc

def login_all():
    # 設置環境變數
    env_setup()
    login_finlab()
    acc = login_fugle()
    return acc
