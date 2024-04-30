import configparser
from linebot import LineBotApi
from linebot.models import TextSendMessage

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

    def send_notification(self, message):
        # 發送消息
        self.line_bot_api.push_message(self.user_id, TextSendMessage(text=message))

# 使用示例
if __name__ == '__main__':
    notification_service = NotificationService()
    notification_service.send_notification("這是來自您的股票交易機器人的測試消息！")
