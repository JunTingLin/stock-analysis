import os
import finlab
from finlab.online.fugle_account import FugleAccount
import logging

def login_finlab(config_path):
    import configparser
    config = configparser.ConfigParser()
    config.read(config_path)

    finlab.login(config['FinLab']['API_TOKEN'])
    logging.info("Logged into FinLab.")

def login_fugle(config_path):
    import configparser
    config = configparser.ConfigParser()
    config.read(config_path)

    os.environ['FUGLE_CONFIG_PATH'] = config_path
    os.environ['FUGLE_MARKET_API_KEY'] = config['FUGLE_MARKET']['API_KEY']

    acc = FugleAccount()
    logging.info("Logged into Fugle.")
    return acc

def login_all(config_path):
    login_finlab(config_path)
    acc = login_fugle(config_path)
    return acc
