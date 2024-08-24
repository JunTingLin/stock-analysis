import os
import logging

class LoggerConfig:
    def __init__(self, log_directory, datetime):
        self.log_directory = log_directory
        self.current_datetime = datetime

    def setup_logging(self):

        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        log_filename = f'{self.current_datetime.strftime("%Y-%m-%d_%H-%M-%S")}.log'
        log_filepath = os.path.join(self.log_directory, log_filename)

        logger = logging.getLogger()

        # 清除已存在的處理程序（避免重複日誌）
        if logger.hasHandlers():
            logger.handlers.clear()

        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(log_filepath, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(file_format)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return log_filepath


