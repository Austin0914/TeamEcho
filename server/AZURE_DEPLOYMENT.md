# Azure Web App 部署指南

## 前置作業

### 1. 準備檔案

確保以下檔案都在 `server` 目錄中：

- `app.py` - 主要應用程式
- `requirements.txt` - Python 依賴
- `startup.sh` - 啟動腳本
- `config.py` - 配置檔案
- `models.py` - 資料庫模型
- `init_db.py` - 資料庫初始化腳本

### 2. 部署前檢查

執行部署前檢查腳本：

```bash
python pre_deploy_check.py
```

## 在 Azure Portal 中創建 Web App

### 1. 創建 Web App

1. 登入 Azure Portal
2. 創建新的 "Web App" 資源
3. 選擇：
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: 選擇靠近用戶的區域

### 2. 配置應用程式設定

在 Web App 的 **Configuration** > **Application settings** 中添加以下環境變數：

```
PGHOST=temechodb.postgres.database.azure.com
PGUSER=austin
PGPORT=5432
PGDATABASE=postgres
PGPASSWORD=~6a@_CEJWerpAS#
GEMINI_API_KEY=AIzaSyC2SwtEZLklTBo4JbJR7p1ninxoU2RwvQM
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-change-this
WEBSITES_ENABLE_APP_SERVICE_STORAGE=false
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### 3. 配置啟動命令

在 **Configuration** > **General settings** 中：

- **Startup Command**: `startup.sh`

## 部署方法

### 方法 1: GitHub Actions (推薦)

1. 將代碼推送到 GitHub
2. 在 Azure Web App 中設定 **Deployment Center**
3. 連接到 GitHub repository
4. Azure 會自動創建 GitHub Actions workflow

### 方法 2: ZIP 部署

1. 壓縮 `server` 目錄中的所有檔案
2. 使用 Azure CLI：

```bash
az webapp deployment source config-zip --resource-group <resource-group> --name <app-name> --src <zip-file-path>
```

### 方法 3: FTP 部署

1. 在 Azure Portal 中獲取 FTP 憑證
2. 使用 FTP 客戶端上傳檔案到 `/home/site/wwwroot/`

## 部署後檢查

### 1. 檢查應用程式日誌

在 Azure Portal 中查看 **Monitoring** > **Log stream**

### 2. 測試健康檢查

訪問：`https://<your-app-name>.azurewebsites.net/health`

### 3. 測試 API 端點

- 用戶註冊：POST `/users`
- 用戶登入：POST `/sessions`
- 表單操作：`/forms` 等

## 常見問題解決

### 1. 應用程式無法啟動

- 檢查 **Log stream** 中的錯誤訊息
- 確認所有環境變數都已正確設定
- 檢查 `requirements.txt` 中的依賴版本

### 2. 資料庫連接失敗

- 確認 Azure PostgreSQL 允許來自 Azure 服務的連接
- 檢查防火牆設定
- 驗證連接字串和憑證

### 3. 靜態檔案問題

- Azure Web App 預設會處理靜態檔案
- 如有問題，檢查 `WEBSITES_ENABLE_APP_SERVICE_STORAGE` 設定

## 生產環境最佳實務

### 1. 安全性

- 使用強密碼作為 `SECRET_KEY`
- 定期輪換資料庫密碼
- 啟用 HTTPS（Azure Web App 預設提供）

### 2. 效能

- 使用 Application Insights 監控效能
- 配置適當的 App Service Plan
- 考慮使用 Azure CDN

### 3. 維護

- 設定自動備份
- 監控應用程式健康狀態
- 定期更新依賴套件
