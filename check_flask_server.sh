#!/bin/bash

FLASK_SERVER_PORT=$1

# 切換目錄到 linebot
cd /home/junting/stock-analysis/linebot

# 檢查 Flask 服務器是否正在運行，如果沒有則啟動
if ! pgrep -f "gunicorn -w 4 -b localhost:$FLASK_SERVER_PORT app:app" > /dev/null; then
    echo "Flask server not running, starting now..."
    nohup gunicorn -w 4 -b localhost:$FLASK_SERVER_PORT app:app &> flask_server.log &
    sleep 5  # 等待幾秒鐘以便檢查是否啟動成功

    # 檢查 gunicorn 是否啟動成功
    if pgrep -f "gunicorn -w 4 -b localhost:$FLASK_SERVER_PORT app:app" > /dev/null; then
        echo "Flask server started."
    else
        echo "Flask server failed to start."
        exit 1  # 中斷腳本執行
    fi
else
    echo "Flask server is already running."
fi