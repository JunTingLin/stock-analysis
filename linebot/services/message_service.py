from jinja2 import Environment, FileSystemLoader

class MessageService:
    def __init__(self, template_path='template', template_file='line_msg.txt'):
        env = Environment(loader=FileSystemLoader(template_path))
        self.template = env.get_template(template_file)

    def render_message(self, data):
        return self.template.render(data=data)
    

if __name__ == '__main__':
    data = {'is_simulation': True, 
            'bank_cash_acc': 52968,
            'positions_acc': [
                {'stock_id': '1101', 'stock_name':'台泥', 'quantity': 0.06, 'close_price': 140.5, 'stock_value': 8430.0}, 
                {'stock_id': '1108', 'stock_name':'幸福', 'quantity': 0.059, 'close_price': 143.0, 'stock_value': 8437.0}, 
                {'stock_id': '8298', 'stock_name':'威睿', 'quantity': 0.048, 'close_price': 176.5, 'stock_value': 8472.0}
            ], 
            'positions_cash_acc': 25339.0, 
            'total_cash': 78307.0, 
            'fund': 42374.4, 
            'positions_next': [
                {'stock_id': '1101', 'stock_name':'台泥', 'quantity': 0.05, 'close_price': 140.5, 'stock_value': 8430.0},
                {'stock_id': '1108', 'stock_name':'幸福', 'quantity': 0.059, 'close_price': 143.0, 'stock_value': 8437.0},
                {'stock_id': '8298', 'stock_name':'威睿', 'quantity': 1, 'close_price': 176.5, 'stock_value': 8472.0}
            ],
            'order_details': [
                {'stock_id': '1101', 'stock_name':'台泥', 'quantity': -0.01, 'limit_price': 140.5},
                {'stock_id': '8298', 'stock_name':'威睿', 'quantity': 0.952, 'limit_price': 176.5}
            ],
            'today': '2024-05-12',
            'is_trading_day': False}
    

    msg_service = MessageService()
    msg = msg_service.render_message(data)
    print(msg)
