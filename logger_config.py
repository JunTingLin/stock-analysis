import os
from datetime import datetime
import logging

def setup_logging():
    # 日誌文件夾的路徑
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)  # 如果目錄不存在，則創建它

    # 創建日誌文件名，包括時間戳以確保唯一性
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = f'{current_time}.log'
    log_filepath = os.path.join(log_directory, log_filename)

    # logging.basicConfig(filename=log_filepath,
    #                     filemode='w',
    #                     level=logging.INFO,
    #                     format='%(asctime)s - %(levelname)s - %(message)s',
    #                     encoding='utf-8')

    # 創建一個 logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 創建文件 file_handler ，用於寫入日誌文件
    file_handler = logging.FileHandler(log_filepath, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    # 創建 stream_handler ，用於輸出到控制台
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(file_format)

    # 添加 handlers 到 logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return log_filepath
    

