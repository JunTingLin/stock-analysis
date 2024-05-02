from jinja2 import Environment, FileSystemLoader

class MessageService:
    def __init__(self, template_path='template', template_file='line_msg.txt'):
        env = Environment(loader=FileSystemLoader(template_path))
        self.template = env.get_template(template_file)

    def render_message(self, data):
        return self.template.render(data=data)
    

if __name__ == '__main__':
    data = {
        'today': '2021-09-01',
        'cash': 100000,
        'position_acc': [{'stock_id': '2330', 'stock_name': '台積電', 'quantity': 100, 'price': 600}],
        'position_next': [{'stock_id': '2317', 'stock_name': '鴻海', 'quantity': 200, 'price': 100}],
        'message': '測試消息',
        'error': ''
    }

    msg_service = MessageService()
    msg = msg_service.render_message(data)
    print(msg)
