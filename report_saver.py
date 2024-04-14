from datetime import datetime
import os
import json


class ReportSaver:
    def __init__(self, report, output_dir='output'):
        self.report = report
        self.output_dir = output_dir

    def create_timestamped_filepath(self, prefix, extension='xlsx'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{prefix}_{timestamp}.{extension}'
        filepath = os.path.join(self.output_dir, filename)
        return filepath

    def ensure_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_report_html(self):
        filepath = self.create_timestamped_filepath('report', 'html')
        self.ensure_directory()
        self.report.display(save_report_path=filepath)
        print(f'Report saved to {filepath}')

    def save_trades_excel(self):
        filepath = self.create_timestamped_filepath('trades_record', 'xlsx')
        # 獲取交易記錄 DataFrame
        trades_df = self.report.get_trades()
        self.ensure_directory()
        trades_df.to_excel(filepath, index=True)
        print(f'Trades record saved to {filepath}')

    def save_dict_to_json(self, data_dict, prefix):
        """將字典數據保存為JSON檔案，檔案名包含時間戳記。"""
        filepath = self.create_timestamped_filepath(prefix, 'json')
        self.ensure_directory()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4)
        print(f'Data saved to {filepath}')

    def save_report_stats_to_json(self, resample='1d', riskfree_rate=0.02):
        """將報告的統計數據保存為JSON檔案。"""
        stats = self.report.get_stats(resample=resample, riskfree_rate=riskfree_rate)
        self.save_dict_to_json(stats, 'report_stats')

    def save_position_info_to_json(self):
        """將報告的持有部位與預期換股資訊保存為JSON檔案。"""
        position_info = self.report.position_info()
        self.save_dict_to_json(position_info, 'position_info')