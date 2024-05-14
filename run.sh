#!/bin/bash

# 切換到專案根目錄
cd /home/junting/stock-analysis

# 激活 miniconda 環境
echo "Activating miniconda environment 'stock-analysis'..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate stock-analysis

# 调用 run_flask.sh
echo "Starting Flask server..."
./linebot/run_flask.sh

# 執行 Python 腳本，使用 expect 處理密碼輸入
echo "Running Python script 'order.py'..."
python order.py


# 退出 miniconda 環境
echo "Deactivating conda environment..."
conda deactivate

echo "Script execution completed."