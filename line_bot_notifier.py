import configparser
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 讀取配置文件
config = configparser.ConfigParser()
config.read('config.simulation.ini')

# 從配置文件中獲取Line Bot的配置信息
channel_access_token = config['LineBot']['ChannelAccessToken']
user_id = config['LineBot']['UserId']

# 初始化LINE Bot API
line_bot_api = LineBotApi(channel_access_token)

def send_line_notification(message):
    # 發送消息
    line_bot_api.push_message(user_id, TextSendMessage(text=message))

if __name__ == '__main__':
    send_line_notification("這是來自您的股票交易機器人的測試消息！")
