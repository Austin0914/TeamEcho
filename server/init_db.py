"""
資料庫初始化腳本
用於創建所有表結構
"""
import os
import sys
import traceback
from flask import Flask
from config import Config
from models import db, User, UserToken, Form, Respondent, Feedback

def create_app():
    """創建 Flask 應用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    return app

def init_database():
    """初始化資料庫表結構"""
    app = create_app()
    
    with app.app_context():
        try:
            print("正在連接到 PostgreSQL 資料庫...")
            # 隱藏密碼以供顯示
            from urllib.parse import quote_plus
            display_uri = Config.SQLALCHEMY_DATABASE_URI.replace(
                quote_plus(Config.PGPASSWORD) if Config.PGPASSWORD else "", 
                "***"
            )
            print(f"連接字串: {display_uri}")
            
            db.engine.connect()
            print("✅ 資料庫連接成功!")
            
            print("正在創建資料庫表...")
            db.create_all()
            print("✅ 資料庫表創建成功!")
            
            from sqlalchemy import text
            result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result]
            
            print("\n📋 已創建的表:")
            for table in sorted(tables):
                print(f"  - {table}")
                
            print(f"\n🎉 資料庫初始化完成! 共創建了 {len(tables)} 個表")
            
        except Exception as e:
            print(f"❌ 資料庫初始化失敗: {str(e)}")
            print(f"詳細錯誤: {traceback.format_exc()}")
            sys.exit(1)

if __name__ == "__main__":
    init_database()
