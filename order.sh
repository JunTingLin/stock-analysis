#!/bin/bash

echo "Activating miniconda environment 'stock-analysis'..."
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate stock-analysis

# 切換至專案根目錄（假設 order_executor.py 放在 jobs 資料夾內）
cd /home/mirlab/stock-analysis

# 獲取當前時間（以 24 小時制，格式為 HHMM）
current_time=$(date +"%H%M")
echo "Current time: $current_time"

# 設置 extra_bid_pct 參數，根據不同時間設定不同參數
if [ "$current_time" -eq "0930" ]; then
    EXTRA_BID_PCT=0
elif [ "$current_time" -eq "1300" ]; then
    EXTRA_BID_PCT=0.01
else
    EXTRA_BID_PCT=0
fi
echo "Extra bid percentage: $EXTRA_BID_PCT"

# 設定使用者與券商參數
USER_NAME="junting"
BROKER_NAME="fugle"

# 如果需要 view-only 模式，則加上 --view_only 參數；否則可留空
VIEW_ONLY_FLAG="--view_only"

# 執行新的 Python 腳本 order_executor.py
echo "Running Python script 'order_executor.py'..."
python jobs/order_executor.py --user_name $USER_NAME --broker_name $BROKER_NAME --extra_bid_pct $EXTRA_BID_PCT $VIEW_ONLY_FLAG

# 退出 miniconda 環境
echo "Deactivating conda environment..."
conda deactivate

echo "Script execution completed."
