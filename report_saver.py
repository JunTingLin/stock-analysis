from datetime import datetime
import os
import json

# 模組級別的輔助函數
def create_timestamped_filepath(prefix, output_dir='output', extension='xlsx'):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{prefix}_{timestamp}.{extension}'
    filepath = os.path.join(output_dir, filename)
    return filepath

def save_report_html(report, output_dir='output'):
    filepath = create_timestamped_filepath('report', output_dir, 'html')
    # 確保輸出資料夾存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    report.display(save_report_path=filepath)
    print(f'Report saved to {filepath}')

def save_trades_excel(report, output_dir='output'):
    filepath = create_timestamped_filepath('trades_record', output_dir, 'xlsx')
    # 獲取交易記錄 DataFrame
    trades_df = report.get_trades()

    # 確保輸出資料夾存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 將交易記錄導出到 Excel 檔案
    trades_df.to_excel(filepath, index=True)
    print(f'Trades record saved to {filepath}')


def save_dict_to_json(data_dict, prefix, output_dir='output'):
    """將字典數據保存為JSON檔案，檔案名包含時間戳記。"""
    filepath = create_timestamped_filepath( prefix, output_dir, 'json')

    # 確保輸出資料夾存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 將字典數據序列化並保存到JSON檔案，並確保中文正確顯示
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=4)
    
    print(f'Data saved to {filepath}')

def save_report_stats_to_json(report, output_dir='output', resample='1d', riskfree_rate=0.02):
    """將報告的統計數據保存為JSON檔案。"""
    stats = report.get_stats(resample=resample, riskfree_rate=riskfree_rate)
    save_dict_to_json(stats, 'report_stats', output_dir)

def save_position_info_to_json(report, output_dir='output'):
    """將報告的持有部位與預期換股資訊保存為JSON檔案。"""
    position_info = report.position_info()
    save_dict_to_json(position_info, 'position_info', output_dir)
