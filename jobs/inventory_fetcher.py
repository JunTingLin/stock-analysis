import logging
from utils.authentication import Authenticator
# from dao.inventory_dao import InventoryDAO
from finlab.online.base_account import Account
from finlab.online.fugle_account import FugleAccount
from finlab.online.sinopac_account import SinopacAccount

logger = logging.getLogger(__name__)

class InventoryFetcherBase():
    def __init__(self, account_obj : Account, user_name):
        self.account = account_obj
        self.user_name = user_name
        # self.inventory_dao = InventoryDAO()
    
    def fetch_and_save(self):
        raw_data = self.fetch_raw_data()
        processed_data = self.process_data(raw_data)
        self.save_to_db(processed_data)
        return processed_data
    
    def fetch_raw_data(self):
        raise NotImplementedError("Subclasses must implement fetch_raw_data")
    
    def process_data(self, raw_data):
        raise NotImplementedError("Subclasses must implement process_data")
    
    def save_to_db(self, processed_data):
        self.inventory_dao.insert_inventory_data(
            user_name = self.user_name,
            broker_name = self.get_broker_name(),
            inventory_data = processed_data
        )
        logger.info(f"Saved inventory data for {self.user_name} using {self.get_broker_name()}")
    
    def get_broker_name(self):
        raise NotImplementedError("Subclasses must implement get_broker_name")


class FugleInventoryFetcher(InventoryFetcherBase):

    def __init__(self, account_obj: FugleAccount, user_name: str):
        super().__init__(account_obj, user_name)

    def fetch_raw_data(self):
        logger.info("Fetching data from Fugle API")
        raw_inventory = self.account.get_inventory()
        return raw_inventory
    
    def process_data(self, raw_data):
        processed_data = {
            
        }
        return processed_data
    
    def get_broker_name(self):
        return "fugle"


class ShioajiInventoryFetcher(InventoryFetcherBase):

    def __init__(self, account_obj: SinopacAccount, user_name: str):
        super().__init__(account_obj, user_name)
    
    def fetch_raw_data(self):
        logger.info("Fetching data from Shioaji API")
        raw_inventory = self.account.get_account_inventory()
        return raw_inventory
    
    def process_data(self, raw_data):
        processed_data = {

        }
        return processed_data
    
    def get_broker_name(self):
        return "shioaji"


class InventoryFetcher:
    """用於建立合適的抓取器實例的工廠類"""
    
    @staticmethod
    def create(user_name, broker_name):
        broker_name = broker_name.lower()
        auth = Authenticator()
        auth.login_finlab()
        account = auth.login_broker(broker_name)
        
        if broker_name == "fugle":
            return FugleInventoryFetcher(account, user_name)
        elif broker_name == "shioaji":
            return ShioajiInventoryFetcher(account, user_name)
        else:
            raise ValueError(f"Unsupported broker: {broker_name}")


def main(user_name, broker_name):
    try:
        fetcher = InventoryFetcher.create(user_name, broker_name)
        inventory_data = fetcher.fetch_and_save()
        logger.info(f"Successfully fetched and saved inventory data for {user_name} using {broker_name}")
        return inventory_data
    except Exception as e:
        logger.exception(f"Error fetching inventory data: {e}")
        raise


if __name__ == "__main__":
    import argparse
    import os
    
    # 確保可以正確執行，無論從哪個目錄運行
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    
    parser = argparse.ArgumentParser(description="Fetch inventory data from broker API")
    parser.add_argument("--user_name", required=True, help="User name (e.g., junting)")
    parser.add_argument("--broker_name", required=True, help="Broker name (e.g., fugle or shioaji)")
    
    args = parser.parse_args()
    main(args.user_name, args.broker_name)