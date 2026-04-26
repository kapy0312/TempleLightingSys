沒問題！把 Python 的確切版本標示清楚是非常好的習慣，這能避免未來換電腦或別人接手時，因為版本不同（例如 Python 3.13 或更舊的版本）而導致 `pywebview` 或 `PyInstaller` 編譯失敗的慘劇。

我已經幫你把版本資訊（`3.12.10`）更新進去，並把 `README.md` 的內容重新整理得更精確。請直接複製以下內容並覆蓋你的 `README.md`：

```markdown
# 正坤點燈管理系統 (Temple Lighting Management System)

這是一個專為宮廟設計的輕量化點燈資料管理系統。採用 Python Flask 作為後端核心，並透過 `pywebview` 封裝為原生桌面應用程式，實現零安裝部署（Portable Application）。

## 核心特性

- **雙重模式 (RBAC)**：
    - **訪客模式**：僅開放資料查詢與顯示全部功能，隱藏所有編輯與刪除接口。
    - **管理員模式**：登入後可進行完整 CRUD（增刪改查）、資料匯入與匯出操作。
- **多姓名渲染邏輯**：姓名欄位支援逗號、空白或分號分隔，前端自動將多組姓名轉化為垂直跨行排列，提升閱讀直覺性。
- **智慧 Excel/CSV 匯入**：支援讀取 `.xlsx` 與 `.csv`，自動識別標頭、合併子編號（如 4.1, 4.2），並以覆蓋模式更新資料庫。
- **CSV 數據匯出**：內建 Excel 相容格式匯出（含 UTF-8 BOM），自動清洗非法字元，確保資料導出不亂碼、不位移。
- **本地零配置**：自動初始化 SQLite 資料庫，隨插隨用。

## 技術棧

| 領域 | 技術 |
| :--- | :--- |
| **後端** | Python 3.12.10, Flask, SQLAlchemy, openpyxl |
| **前端** | Vanilla JavaScript, Bootstrap 5, Bootstrap Icons |
| **資料庫** | SQLite (檔案式資料庫) |
| **桌面化** | pywebview (Edge Chromium 核心) |
| **打包工具** | PyInstaller |

## 專案結構

```text
TempleLightingSys/
├── main.py              # 桌面應用程式啟動入口 (含執行緒管理與防文字選取設定)
├── app.py               # Flask RESTful API、資料庫模型與檔案解析邏輯
├── templates/
│   └── index.html       # 前端 UI 佈局 (Bootstrap 5 + Glassmorphism 設計)
├── static/
│   ├── background.png   # 系統背景圖
│   └── js/
│       └── app.js       # 前端業務邏輯與 API 互動
├── favicon.ico          # 應用程式圖示
└── requirements.txt     # 相依套件清單
```

---

## 開發環境與常用指令備忘錄

⚠️ **執行以下指令前，請確保終端機顯示 `(venv)`，且位於專案根目錄。**

### 1. 初始化與環境安裝
1. **版本要求**：必須使用 **Python 3.12.10** (確保 `pythonnet` 與套件相容性，切勿使用過新或測試版)。
2. **建立與啟動虛擬環境**：
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **一鍵安裝依賴套件**：
   ```powershell
   pip install -r requirements.txt
   ```
   > 核心依賴清單參考：`Flask==3.0.2`, `Flask-SQLAlchemy==3.1.1`, `pywebview==4.4.1`, `pyinstaller==6.4.0`, `Werkzeug==3.0.1`, `openpyxl==3.1.2`

### 2. 日常開發與測試
啟動 Flask 伺服器並開啟應用程式視窗進行測試：
```powershell
python main.py
```

### 3. 環境與套件管理
當安裝了新套件或需要檢查環境配置時：
* **檢查已安裝的套件清單**：
  ```powershell
  pip list
  ```
* **導出/更新套件清單至 requirements.txt**：
  ```powershell
  pip freeze > requirements.txt
  ```

### 4. 軟體正式打包 (PyInstaller)
系統功能確認無誤後，將專案打包成單一 `.exe` 執行檔，以利交付給使用者：
```powershell
pyinstaller -F -w --clean --name "正坤點燈管理系統" --icon="favicon.ico" --add-data "templates;templates" --add-data "static;static" main.py
```
> 💡 **打包與交付說明**：
> * 執行成功後，產出的執行檔會位於 **`dist`** 資料夾內。
> * 交付給使用者時，僅需提供 `正坤點燈管理系統.exe`。若需保留舊有的點燈資料，請將舊的 `temple_data.db` 放在與 `.exe` 同一個資料夾中即可讀取。
```

這份文件現在非常完整且專業了！還有什麼需要補充或修改的地方嗎？