import datetime
from dao.order_dao import OrderDAO

class OrderService:
    def __init__(self, db_path="data_prod.db"):
        self.order_dao = OrderDAO(db_path=db_path)

    def get_order_history(self, account_id, query_date):
        raw_orders = self.order_dao.get_orders_by_account_and_date(account_id, query_date)
        filtered_orders = []
        for order in raw_orders:
            filtered_orders.append({
                "order_timestamp": order.get("order_timestamp"),
                "action": order.get("action"),
                "stock_id": order.get("stock_id"),
                "stock_name": order.get("stock_name"),
                "quantity": order.get("quantity"),
                "price": order.get("price"),
                "extra_bid_pct": order.get("extra_bid_pct"),
                "order_condition": order.get("order_condition"),
            })
        return filtered_orders
    
if __name__ == "__main__":
    order_service = OrderService()
    date_str = f"2025-03-05"
    query_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    orders = order_service.get_order_history(account_id=1, query_date=query_date)
    print(orders)