#!/bin/bash

# 切換到腳本所在目錄
cd /home/junting/stock-analysis

# 激活 miniconda 環境
echo "Activating miniconda environment 'stock-analysis'..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate stock-analysis

# 檢查 Flask 服務器是否正在運行，如果沒有則啟動
if ! pgrep -f "gunicorn -w 4 -b localhost:5000 webhook_handler:app" > /dev/null; then
    echo "Flask server not running, starting now..."
    nohup gunicorn -w 4 -b localhost:5000 webhook_handler:app &> flask_server.log &
    echo "Flask server started."
else
    echo "Flask server is already running."
fi

# 執行 Python 腳本，使用 expect 處理密碼輸入
echo "Running Python script 'order.py'..."
expect -c "
spawn python order.py
expect \"Please enter password for encrypted keyring:\"
send \"${KEYRING_PASSWORD}\r\"
interact
"

# 退出 miniconda 環境
echo "Deactivating conda environment..."
conda deactivate

echo "Script execution completed."
