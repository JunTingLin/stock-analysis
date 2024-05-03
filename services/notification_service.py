import configparser
from linebot import LineBotApi
from linebot.models import TextSendMessage
import json
import os

class NotificationService:
    def __init__(self, config_path='config/config.simulation.ini'):
        # 讀取配置文件
        config = configparser.ConfigParser()
        config.read(config_path)
        # 從配置文件中獲取Line Bot的配置信息
        self.channel_access_token = config['LineBot']['ChannelAccessToken']
        self.user_id = config['LineBot']['UserId']
        # 初始化LINE Bot API
        self.line_bot_api = LineBotApi(self.channel_access_token)
        self.user_ids_file = 'user_ids.json' 

    def send_notification_to_user(self, user_id, message):
        self.line_bot_api.push_message(user_id, TextSendMessage(text=message))

    def send_notification_to_developer(self, message):
        self.line_bot_api.push_message(self.user_id, TextSendMessage(text=message))

    def _load_user_ids(self):
        if os.path.exists(self.user_ids_file):
            with open(self.user_ids_file, 'r') as file:
                user_ids = json.load(file)
                return user_ids
        return []
    
    def send_notification_to_all_users(self, message):
        user_ids = self._load_user_ids()
        for user_id in user_ids:
            self.line_bot_api.push_message(user_id, TextSendMessage(text=message))

# 使用示例
if __name__ == '__main__':
    notification_service = NotificationService()
    
