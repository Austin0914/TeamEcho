#!/usr/bin/env python3
"""
部署前檢查腳本
確保所有必要的設定和依賴都正確
"""
import os
import sys

def check_environment_variables():
    """檢查必要的環境變數"""
    required_vars = [
        'PGHOST', 'PGUSER', 'PGPORT', 'PGDATABASE', 'PGPASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要的環境變數: {', '.join(missing_vars)}")
        return False
    
    print("✅ 所有必要的環境變數都已設定")
    return True

def check_database_connection():
    """檢查資料庫連接"""
    try:
        from config import Config
        import psycopg2
        from urllib.parse import quote_plus
        
        # 測試資料庫連接
        conn = psycopg2.connect(
            host=Config.PGHOST,
            user=Config.PGUSER,
            port=Config.PGPORT,
            database=Config.PGDATABASE,
            password=Config.PGPASSWORD,
            sslmode='require'
        )
        conn.close()
        print("✅ 資料庫連接測試成功")
        return True
    except Exception as e:
        print(f"❌ 資料庫連接失敗: {e}")
        return False

def check_dependencies():
    """檢查必要的模組依賴"""
    required_modules = [
        'flask', 'flask_cors', 'flask_sqlalchemy', 
        'sqlalchemy', 'psycopg2', 'dotenv'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ 缺少必要的模組: {', '.join(missing_modules)}")
        return False
    
    print("✅ 所有必要的模組都已安裝")
    return True

def check_files():
    """檢查必要的檔案"""
    required_files = [
        'app.py', 'config.py', 'models.py', 'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要的檔案: {', '.join(missing_files)}")
        return False
    
    print("✅ 所有必要的檔案都存在")
    return True

def main():
    """執行所有檢查"""
    print("=== Azure Web App 部署前檢查 ===\n")
    
    checks = [
        ("檢查檔案", check_files),
        ("檢查依賴模組", check_dependencies),
        ("檢查環境變數", check_environment_variables),
        ("檢查資料庫連接", check_database_connection)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"{name}...")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 所有檢查都通過！可以進行部署。")
        sys.exit(0)
    else:
        print("❌ 部分檢查失敗，請修復問題後再部署。")
        sys.exit(1)

if __name__ == "__main__":
    main()
