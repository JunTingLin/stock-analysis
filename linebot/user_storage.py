import json

config_path = 'config.json'

def save_user_id(user_id):
    """保存 user_id 到 JSON 文件"""
    with open(config_path, 'r') as file:
        config = json.load(file)
    
    user_ids = config['LineBot']['AllUserIds']

    if user_id not in user_ids:
        user_ids.append(user_id)
        config['LineBot']['AllUserIds'] = user_ids
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)

if __name__ == '__main__':
    save_user_id("12345")
