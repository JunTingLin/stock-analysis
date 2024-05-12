import unittest
import os
import json
import sys

# 將上級目錄新增至模組搜尋路徑中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from user_storage import save_user_id

class TestUserStorage(unittest.TestCase):
    
    def test_save_user_id(self):
        user_ids_file = 'user_ids.json'
    
        # 測試前清理環境
        if os.path.exists(user_ids_file):
            os.remove(user_ids_file)
        
        # 測試save_user_id功能
        test_user_id = "12345"
        save_user_id(test_user_id)
        
        # 檢查文件是否存在
        self.assertTrue(os.path.exists(user_ids_file))
        
        # 檢查user_id是否正確保存
        with open(user_ids_file, 'r') as file:
            user_ids = json.load(file)
            self.assertIn(test_user_id, user_ids)
        
        # 測試完成後清理文件
        if os.path.exists(user_ids_file):
            os.remove(user_ids_file)

if __name__ == '__main__':
    unittest.main()
