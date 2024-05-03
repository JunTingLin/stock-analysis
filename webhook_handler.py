from flask import Flask, request, abort
from linebot import WebhookHandler
from linebot import LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import logging
from services.notification_service import NotificationService
import configparser
import user_storage

config_path = 'config/config.simulation.ini'
config = configparser.ConfigParser()
config.read(config_path)

app = Flask(__name__)
handler = WebhookHandler(config['LineBot']['ChannelSecret'])
channel_access_token = config['LineBot']['ChannelAccessToken']
line_bot_api = LineBotApi(channel_access_token)

notification_service = NotificationService()

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取請求頭的X-Line-Signature
    signature = request.headers['X-Line-Signature']

    # 獲取請求體作為文本
    body = request.get_data(as_text=True)
    logging.info("Request body: " + body)

    # 處理Webhook體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logging.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        abort(500)

    return 'OK'


@handler.add(FollowEvent)
def handle_follow(event):
    logging.info(f"Got FollowEvent: {event}")
    try:
        user_id = event.source.user_id
        user_storage.save_user_id(user_id)
        notification_service.send_notification_to_user(user_id, "感謝添加為好友！")
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == '測試':
        reply_text = '測試喔'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    else:
        logging.info(f"Received message not handled: {text}")

if __name__ == "__main__":
    app.run()
