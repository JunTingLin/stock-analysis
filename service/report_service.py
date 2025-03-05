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
        # YYYY-MM-DD_HH-MM-SS.html
        match = re.match(r"(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})\.html", filename)
        if match:
            year, month, day, hour, minute, second = match.groups()
            return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        return None

    def get_available_timestamps(self, account_name):
        files = self.list_report_files(account_name)
        timestamps = []
        for f in files:
            dt = self.parse_timestamp_from_filename(f)
            if dt:
                timestamps.append(dt)
        timestamps.sort(reverse=True)  # 遞減排序
        return timestamps

    def get_available_years(self, account_name):
        timestamps = self.get_available_timestamps(account_name)
        years = sorted({dt.year for dt in timestamps}, reverse=True)  # 遞減排序
        return [{'label': str(y), 'value': str(y)} for y in years]

    def get_available_months(self, account_name, year):
        timestamps = self.get_available_timestamps(account_name)
        months = sorted({dt.month for dt in timestamps if dt.year == int(year)}, reverse=True)  # 遞減排序
        return [{'label': f"{m:02d}", 'value': f"{m:02d}"} for m in months]

    def get_available_days(self, account_name, year, month):
        timestamps = self.get_available_timestamps(account_name)
        days = sorted({dt.day for dt in timestamps if dt.year == int(year) and dt.month == int(month)}, reverse=True)  # 遞減排序
        return [{'label': f"{d:02d}", 'value': f"{d:02d}"} for d in days]

    def get_available_times(self, account_name, year, month, day):
        timestamps = self.get_available_timestamps(account_name)
        times = sorted(
            {dt.strftime("%H-%M-%S") for dt in timestamps if dt.year == int(year) and dt.month == int(month) and dt.day == int(day)}, 
            reverse=True
        )
        return [{'label': t, 'value': t} for t in times]

    def get_report_url(self, account_name, year, month, day, time_str):
        """
        回傳報表檔案的 URL，假設 Dash 自動將 assets/ 目錄作為靜態檔案來源。
        """
        filename = f"{year}-{month}-{day}_{time_str}.html"
        url = f"/assets/report_finlab/{account_name}/{filename}"
        report_path = os.path.join(self.get_account_report_directory(account_name), filename)
        if os.path.exists(report_path):
            return url
        return ""
