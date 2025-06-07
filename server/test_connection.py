"""
簡單的資料庫連接測試
"""
import os
import psycopg2
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_connection():
    try:
        # 獲取連接參數
        host = os.getenv('PGHOST')
        user = os.getenv('PGUSER')
        port = os.getenv('PGPORT', '5432')
        database = os.getenv('PGDATABASE')
        password = os.getenv('PGPASSWORD')
        
        print(f"正在連接到 PostgreSQL...")
        print(f"Host: {host}")
        print(f"User: {user}")
        print(f"Port: {port}")
        print(f"Database: {database}")
        print(f"Password: {'*' * len(password) if password else 'None'}")
        
        # 連接到資料庫
        conn = psycopg2.connect(
            host=host,
            user=user,
            port=port,
            database=database,
            password=password,
            sslmode='require'
        )
        
        # 測試查詢
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("✅ 資料庫連接成功!")
        print(f"PostgreSQL 版本: {version[0]}")
        
        # 關閉連接
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 資料庫連接失敗: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
