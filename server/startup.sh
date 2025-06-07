#!/bin/bash

# Azure Web App 啟動腳本
echo "Starting TeamEcho Flask application..."

# 設置環境變數
export FLASK_APP=app.py
export FLASK_ENV=production

# 初始化資料庫表（如果需要）
echo "Checking database initialization..."
python init_db.py || echo "Database tables may already exist"

# 啟動 Flask 應用
echo "Starting Flask server..."
gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 600 app:app
