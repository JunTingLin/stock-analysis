import json
from linebot import LineBotApi
from linebot.models import TextSendMessage

class NotificationService:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        with open(self.config_path, 'r') as file:
            config = json.load(file)
        self.channel_access_token = config['LineBot']['ChannelAccessToken']
        self.dev_user_ids = config['LineBot']['DevUserIds']
        self.all_user_ids = config['LineBot']['AllUserIds']
        self.line_bot_api = LineBotApi(self.channel_access_token)

    def send_notification_to_user(self, user_id, message):
        self.line_bot_api.push_message(user_id, TextSendMessage(text=message))

    def send_notification_to_developers(self, message):
        self._load_config()
        for user_id in self.dev_user_ids:
            self.line_bot_api.push_message(user_id, TextSendMessage(text=message))

    def send_notification_to_all_users(self, message):
        self._load_config()
        for user_id in self.all_user_ids:
            self.line_bot_api.push_message(user_id, TextSendMessage(text=message))

# 使用示例
if __name__ == '__main__':
    notification_service = NotificationService()
    # notification_service.send_notification_to_developers('Hello, developer!')
    # notification_service.send_notification_to_all_users('Hello, all users!')
