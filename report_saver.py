from datetime import datetime
import os

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
