import requests
import logging

class LineNotifier:
    def __init__(self, token):
        self.token = token

    def send_notification(self, message):
        url = "https://notify-api.line.me/api/notify"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        data = {
            "message": message
        }
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            logging.info(f"LINE Notification sent successfully: {response.text}")
        else:
            logging.error(f"Failed to send LINE Notification: {response.status_code} {response.text}")

        return response.status_code, response.text

if __name__ == "__main__":
    from config_loader import ConfigLoader
    config_loader = ConfigLoader()
    config_loader.load_env_vars()
    line_token = config_loader.get_env_var("LINE_NOTIFY_TOKEN")
    notifier = LineNotifier(line_token)
    notifier.send_notification("Hello, World!")