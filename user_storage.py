import os
import json

user_ids_file = 'user_ids.json'

def save_user_id(user_id):
    """保存 user_id 到 JSON 文件"""
    if os.path.exists(user_ids_file):
        with open(user_ids_file, 'r') as file:
            user_ids = json.load(file)
    else:
        user_ids = []

    if user_id not in user_ids:
        user_ids.append(user_id)
        with open(user_ids_file, 'w') as file:
            json.dump(user_ids, file)

if __name__ == '__main__':
    save_user_id("12345")