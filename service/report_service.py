import os
import re
import datetime

class ReportService:
    def __init__(self, base_directory="assets/report_finlab"):
        self.base_directory = base_directory

    def get_account_report_directory(self, account_name):
        return os.path.join(self.base_directory, account_name)

    def list_report_files(self, account_name):
        report_dir = self.get_account_report_directory(account_name)
        if not os.path.exists(report_dir):
            return []
        files = [f for f in os.listdir(report_dir) if f.endswith(".html")]
        return files

    def parse_timestamp_from_filename(self, filename):
        # strategy_class_name_YYYY-MM-DD_HH-MM-SS.html
        match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.html$", filename)
        if match:
            datetime_str = match.group(1)
            try:
                return datetime.datetime.strptime(datetime_str, '%Y-%m-%d_%H-%M-%S')
            except ValueError:
                return None
        return None

    def get_report_url_by_date(self, account_name, date):
        """
        返回指定日期最新的報告URL
        
        Args:
            account_name (str): 帳戶名稱
            date (datetime.date): 要獲取報告的日期
            
        Returns:
            str: 報告的URL，如果沒有可用的報告則返回空字符串
        """
        files = self.list_report_files(account_name)
        date_files = []
        
        # 搜索匹配指定日期的文件
        date_str = date.strftime('%Y-%m-%d')
        for file in files:
            if date_str in file:  # 檢查文件名中是否包含日期字符串
                timestamp = self.parse_timestamp_from_filename(file)
                if timestamp and timestamp.date() == date:
                    date_files.append((timestamp, file))
        
        if not date_files:
            return ""
        
        # 獲取該日期最新的文件
        most_recent_file = sorted(date_files, key=lambda x: x[0], reverse=True)[0][1]
        
        # 返回URL
        url = f"/assets/report_finlab/{account_name}/{most_recent_file}"
        
        return url
