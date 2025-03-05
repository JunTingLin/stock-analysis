from dao.account_dao import AccountDAO

class AccountService:
    def __init__(self, db_path="data_prod.db"):
        self.account_dao = AccountDAO(db_path=db_path)

    def get_order_history(self, account_name, broker, user_name, query_date):
        # 取得 account_id，若不存在則 AccountDAO 會自動新增
        account_id = self.account_dao.get_account_id(account_name, broker, user_name)
        orders = self.order_dao.get_orders_by_account_and_date(account_id, query_date)
        return orders
    
    def get_all_accounts(self):
        accounts = self.account_dao.get_all_accounts()
        return accounts
