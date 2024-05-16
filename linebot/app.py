# 標準庫導入
import configparser
import logging

# 第三方庫導入
from flask import Flask, request, jsonify, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, MessageEvent, TextMessage, TextSendMessage

# 本地應用導入
from services.notification_service import NotificationService
from services.message_service import MessageService
import user_storage

config_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_path)

app = Flask(__name__)

channel_secret = config["LineBot"]['ChannelSecret']
channel_access_token = config["LineBot"]['ChannelAccessToken']

handler = WebhookHandler(channel_secret)
line_bot_api = LineBotApi(channel_access_token)

notification_service = NotificationService()
message_service = MessageService() 

@app.route("/")
def hello():
    return "This is the webhook handler for the Line Bot!"

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


@app.route('/notify_dev', methods=['POST'])
def notify_dev():
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({"error": "Missing message"}), 400

    try:
        rendered_message = message_service.render_message(message)
        notification_service.send_notification_to_developer(rendered_message)
        return jsonify({"success": True}), 200
    except Exception as e:
        logging.error(f"Exception in notify_dev: {str(e)}")
        return jsonify({"error": "Notification failed"}), 500
    
@app.route('/notify_all', methods=['POST'])
def notify_all():
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({"error": "Missing message"}), 400

    try:
        rendered_message = message_service.render_message(message)
        notification_service.send_notification_to_all_users(rendered_message)
        return jsonify({"success": True}), 200
    except Exception as e:
        logging.error(f"Exception in notify_all: {str(e)}")
        return jsonify({"error": "Notification failed"}), 500



if __name__ == "__main__":
    app.run()
