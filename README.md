# 正坤點燈管理系統 (Temple Lighting Management System)

這是一個專為宮廟設計的輕量化點燈資料管理系統。採用 Python Flask 作為後端核心，並透過 `pywebview` 封裝為原生桌面應用程式，實現零安裝部署（Portable Application）。

## 核心特性

- **雙重模式 (RBAC)**：
    - **訪客模式**：僅開放資料查詢與顯示全部功能，隱藏所有編輯與刪除接口。
    - **管理員模式**：登入後可進行完整 CRUD（增刪改查）操作。
- **多姓名渲染邏輯**：姓名欄位支援逗號或空白分隔，前端自動將多組姓名轉化為垂直跨行排列，提升閱讀直覺性。
- **CSV 數據匯出**：內建 Excel 相容格式匯出（含 UTF-8 BOM），自動清洗非法字元，確保資料導出不亂碼、不位移。
- **本地零配置**：自動初始化 SQLite 資料庫，隨插隨用。

## 技術棧

| 領域 | 技術 |
| :--- | :--- |
| **後端** | Python 3.12, Flask, SQLAlchemy |
| **前端** | Vanilla JavaScript, Bootstrap 5, Bootstrap Icons |
| **資料庫** | SQLite (檔案式資料庫) |
| **桌面化** | pywebview (Edge Chromium 核心) |
| **打包工具** | PyInstaller |

## 專案結構

```text
TempleLightingSys/
├── main.py              # 桌面應用程式啟動入口 (含執行緒管理)
├── app.py               # Flask RESTful API 與資料庫模型
├── templates/
│   └── index.html       # 前端 UI 佈局 (Bootstrap 5)
├── static/
│   └── js/
│       └── app.js       # 前端業務邏輯與 API 互動
├── favicon.ico          # 應用程式圖示
└── requirements.txt     # 相依套件清單
```

## 開發環境建置

1. **版本要求**：必須使用 Python 3.12.x (確保 `pythonnet` 套件相容性)。
2. **建立虛擬環境**：
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **安裝依賴**：
   ```powershell
   pip install Flask==3.0.2 Flask-SQLAlchemy==3.1.1 pywebview==4.4.1 pyinstaller==6.4.0 Werkzeug==3.0.1
   ```
4. **啟動測試**：
   ```powershell
   python main.py
   ```

## 生產環境打包 (Build)

執行以下指令將專案打包成單一 `.exe` 檔案。打包完成後，執行檔位於 `dist/` 目錄下。

```powershell
pyinstaller -F -w --clean --name "正坤點燈管理系統" --icon="favicon.ico" --add-data "templates;templates" --add-data "static;static" main.py
```

### 打包參數說明：
- `-F`：產生單一執行檔。
- `-w`：執行時不顯示後台終端機黑框。
- `--add-data`：將靜態網頁資源封裝進 `.exe` 暫存區（透過 `sys._MEIPASS` 存取）。

## 維護與備份

- **資料庫備份**：系統啟動後會於執行檔同層生成 `temple_data.db`。若要移轉資料，僅需複製此檔案即可。
- **預設帳密**：
    - 帳號：`admin`
    - 密碼：`admin123`

## 授權
由 Kevin Lai 開發維護。基於 Time-to-Solution 指標優化，適用於輕量化工業與宗教管理場景。