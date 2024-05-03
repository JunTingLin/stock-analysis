import unittest
from unittest.mock import Mock, patch
from linebot.models import FollowEvent
from linebot.models.sources import SourceUser  # 使用新的类
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from webhook_handler import handle_follow

class TestWebhookHandler(unittest.TestCase):
    def test_handle_follow(self):
        event_mock = Mock(spec=FollowEvent)
        event_mock.source = SourceUser(user_id="1234567890")
        
        with patch('webhook_handler.user_storage') as mock_user_storage, \
            patch('webhook_handler.notification_service.send_notification_to_user') as mock_send_notification:
            handle_follow(event_mock)
            
            mock_user_storage.assert_called_once_with("1234567890")
            mock_send_notification.assert_called_once_with("1234567890", "感謝添加為好友！")

if __name__ == '__main__':
    unittest.main()