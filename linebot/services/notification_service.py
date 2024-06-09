import json
from linebot import LineBotApi
from linebot.models import TextSendMessage

class NotificationService:
    def __init__(self, config_path='config.json'):
        # 讀取配置文件
        with open(config_path, 'r') as file:
            config = json.load(file)
        # 從配置文件中獲取Line Bot的配置信息
        self.channel_access_token = config['LineBot']['ChannelAccessToken']
        self.dev_user_ids = config['LineBot']['DevUserIds']
        self.all_user_ids = config['LineBot']['AllUserIds']
        # 初始化LINE Bot API
        self.line_bot_api = LineBotApi(self.channel_access_token)

    def send_notification_to_user(self, user_id, message):
        self.line_bot_api.push_message(user_id, TextSendMessage(text=message))

    def send_notification_to_developers(self, message):
        for user_id in self.dev_user_ids:
            self.line_bot_api.push_message(user_id, TextSendMessage(text=message))

    def send_notification_to_all_users(self, message):
        for user_id in self.all_user_ids:
            self.line_bot_api.push_message(user_id, TextSendMessage(text=message))

# 使用示例
if __name__ == '__main__':
    notification_service = NotificationService()
    # notification_service.send_notification_to_developers('Hello, developer!')
    # notification_service.send_notification_to_all_users('Hello, all users!')
