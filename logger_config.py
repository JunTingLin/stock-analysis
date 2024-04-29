import os
from datetime import datetime
import logging

def setup_logging():
# 日誌文件夾的路徑
    log_directory = 'log'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)  # 如果目錄不存在，則創建它

    # 創建日誌文件名，包括時間戳以確保唯一性
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = f'{current_time}.log'
    log_filepath = os.path.join(log_directory, log_filename)

    # 設置日誌記錄配置
    logging.basicConfig(filename=log_filepath,
                        filemode='w',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        encoding='utf-8')
