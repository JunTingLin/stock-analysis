import logging
import requests
import os

def notify_users(config_file_name, trading_info):
    try:
        # 讀取環境變數中的 Flask 伺服器端口號
        flask_server_port = os.getenv('FLASK_SERVER_PORT')

        # 根據配置文件名設置通知 URL
        if config_file_name == 'config.simulation.ini':
            url = f'http://127.0.0.1:{flask_server_port}/notify_dev'
        else:
            url = f'http://127.0.0.1:{flask_server_port}/notify_all'

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
