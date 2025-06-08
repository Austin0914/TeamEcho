"""
測試 TeamEcho API 端點
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """測試健康檢查端點"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_user_registration():
    """測試用戶註冊"""
    try:
        user_data = {
            "name": "測試用戶",
            "email": "test@example.com",
            "password": "testpassword"
        }
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        print(f"User Registration: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [201, 409]  # 201 = success, 409 = already exists
    except Exception as e:
        print(f"User registration failed: {e}")
        return False

def test_user_login():
    """測試用戶登入"""
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        response = requests.post(f"{BASE_URL}/sessions", json=login_data)
        print(f"User Login: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return response.json().get('access_token')
        else:
            print(f"Response: {response.json()}")
            return None
    except Exception as e:
        print(f"User login failed: {e}")
        return None

def main():
    """執行所有測試"""
    print("=== TeamEcho API 測試 ===")
    
    print("\n1. 測試健康檢查...")
    if test_health():
        print("✅ 健康檢查通過")
    else:
        print("❌ 健康檢查失敗")
        return
    
    print("\n2. 測試用戶註冊...")
    if test_user_registration():
        print("✅ 用戶註冊功能正常")
    else:
        print("❌ 用戶註冊失敗")
        return
    
    print("\n3. 測試用戶登入...")
    token = test_user_login()
    if token:
        print("✅ 用戶登入成功")
        print(f"Access Token: {token[:20]}...")
    else:
        print("❌ 用戶登入失敗")
        return
    
    print("\n🎉 所有基本測試通過！")

if __name__ == "__main__":
    main()
