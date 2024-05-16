import logging
import requests

def notify_users(config_file_name, trading_info):
    try:
        if config_file_name == 'config.simulation.ini':
            url = 'http://127.0.0.1:5000/notify_dev'
        else:
            url = 'http://127.0.0.1:5000/notify_all'

        payload = {'message': trading_info.data}

        # 發送 POST 請求通知使用者
        response = requests.post(url, json=payload)
        
        # 檢查回應狀態碼
        if response.status_code == 200:
            logging.info("通知使用者成功")
        else:
            logging.error("通知使用者失敗")
            logging.error(f"回應碼: {response.status_code}")
            logging.error(f"回應訊息: {response.text}")

    except requests.exceptions.RequestException as e:
        # 捕捉 requests 相關的異常
        logging.error("通知使用者失敗，請求出現異常")
        logging.error(str(e))
    except Exception as e:
        # 捕捉所有其他異常
        logging.error("通知使用者失敗，出現未預期的錯誤")
        logging.error(str(e))
