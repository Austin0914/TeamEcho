"""
資料庫配置
"""
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Config:    # PostgreSQL 連接配置
    PGHOST = os.getenv('PGHOST')
    PGUSER = os.getenv('PGUSER') 
    PGPORT = os.getenv('PGPORT', '5432')
    PGDATABASE = os.getenv('PGDATABASE')
    PGPASSWORD = os.getenv('PGPASSWORD')
    
    # 構建 PostgreSQL 連接字串 (對密碼進行 URL 編碼)
    encoded_password = quote_plus(PGPASSWORD) if PGPASSWORD else ""
    SQLALCHEMY_DATABASE_URI = f"postgresql://{PGUSER}:{encoded_password}@{PGHOST}:{PGPORT}/{PGDATABASE}?sslmode=require"
    
    # SQLAlchemy 設定
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # 連接健康檢查
        'pool_recycle': 300,    # 連接回收時間（秒）
        'connect_args': {
            'sslmode': 'require',
            'options': '-c timezone=UTC'
        }
    }
    
    # Flask 設定
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    @classmethod
    def validate_config(cls):
        """驗證必要的配置是否存在"""
        required_vars = ['PGHOST', 'PGUSER', 'PGDATABASE', 'PGPASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"缺少必要的環境變數: {', '.join(missing_vars)}")
        
        return True
