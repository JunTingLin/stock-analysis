#!/bin/bash

# 切換到腳本所在目錄
cd /home/junting/stock-analysis

# 激活 miniconda 環境
echo "Activating miniconda environment 'stock-analysis'..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate stock-analysis

# 檢查 Flask 服務器是否正在運行，如果沒有則啟動
if ! pgrep -f "gunicorn -w 4 -b localhost:5000 your_flask_app:app" > /dev/null; then
    echo "Flask server not running, starting now..."
    nohup gunicorn -w 4 -b localhost:5000 your_flask_app:app &> flask_server.log &
    echo "Flask server started."
else
    echo "Flask server is already running."
fi

# 執行 Python 腳本
echo "Running Python script 'order.py'..."
python order.py

# 退出 miniconda 環境
echo "Deactivating conda environment..."
conda deactivate

echo "Script execution completed."
