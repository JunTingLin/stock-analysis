#!/bin/bash

# 激活 miniconda 環境
echo "Activating miniconda environment 'stock-analysis'..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate stock-analysis

# 檢查 Flask 服務器是否正在運行，如果沒有則啟動
if ! pgrep -f "gunicorn -w 4 -b localhost:5000 app:app" > /dev/null; then
    echo "Flask server not running, starting now..."
    nohup gunicorn -w 4 -b localhost:5000 app:app &> flask_server.log &
    echo "Flask server started."
else
    echo "Flask server is already running."
fi
