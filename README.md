# 正坤點燈管理系統 (Temple Lighting Management System)

> 專為宮廟設計的輕量化點燈資料管理系統，以 Python Flask 驅動後端，並透過 `pywebview` 封裝為免安裝的原生桌面應用程式。

---

## ✨ 功能特色

| 功能 | 說明 |
|------|------|
| **角色權限控制 (RBAC)** | 訪客模式僅供關鍵字查詢；管理員登入後開放完整 CRUD、顯示全部、匯入匯出 |
| **多姓名渲染** | 姓名欄支援逗號、空白分隔，前端自動轉為垂直排列顯示 |
| **智慧匯入（累加模式）** | 支援 `.xlsx` / `.csv`，自動識別標頭、合併子編號（如 4.1, 4.2），新增至現有資料，不覆蓋原有紀錄 |
| **CSV 匯出** | 含 UTF-8 BOM，確保 Excel 在繁體中文環境下開啟不亂碼 |
| **零配置部署** | 自動初始化 SQLite 資料庫，隨插即用，無需額外設定 |
| **關鍵字搜尋** | 支援依姓名或壇名進行模糊搜尋，Enter 鍵直接觸發 |
| **台中市政府風格 UI** | 深藍 + 紅色政府系配色，含 Logo、搜尋面板、資料表格 |
| **金額保護** | 未登入狀態下金額欄位自動模糊遮蔽，登入後還原顯示 |

---

## 🔐 權限對照表

| 功能 | 訪客 | 管理員 |
|------|:----:|:------:|
| 關鍵字查詢 | ✅ | ✅ |
| 匯出 CSV | ✅ | ✅ |
| 查看金額明細 | ❌ | ✅ |
| 顯示全部清單 | ❌ | ✅ |
| 新增紀錄 | ❌ | ✅ |
| 編輯紀錄 | ❌ | ✅ |
| 刪除紀錄 | ❌ | ✅ |
| 匯入 CSV / XLSX | ❌ | ✅ |

---

## 🛠️ 技術棧

| 領域 | 技術 |
|------|------|
| **後端** | Python 3.12.10, Flask 3.0.2, Flask-SQLAlchemy 3.1.1, openpyxl 3.1.2 |
| **前端** | Vanilla JavaScript, Bootstrap 5, Bootstrap Icons, Noto Sans TC |
| **資料庫** | SQLite（檔案式，零配置） |
| **桌面化** | pywebview 4.4.1（Edge Chromium 核心） |
| **打包工具** | PyInstaller 6.4.0 |

---

## 📁 專案結構

```
TempleLightingSys/
├── main.py                  # 桌面應用程式啟動入口（執行緒管理）
├── app.py                   # Flask RESTful API、資料庫模型、檔案解析邏輯
├── build.bat                # 一鍵打包腳本
├── templates/
│   └── index.html           # 前端 UI（台中市政府風格）
├── static/
│   ├── intdex_logo.png      # 宮廟 Logo
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   └── bootstrap-icons.min.css
│   └── js/
│       └── bootstrap.bundle.min.js
├── favicon.ico              # 應用程式圖示
├── requirements.txt         # 相依套件清單
└── temple_data.db           # SQLite 資料庫（執行後自動產生）
```

---

## 🚀 快速開始

> ⚠️ **執行以下指令前，請確保終端機顯示 `(venv)`，且位於專案根目錄。**

### 1. 環境需求

- **Python 3.12.10**（必須，確保 `pythonnet` 與套件相容性）
- Windows 作業系統（pywebview 使用 Edge Chromium 核心）

### 2. 建立虛擬環境

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. 安裝相依套件

```powershell
pip install -r requirements.txt
```

### 4. 啟動應用程式

```powershell
# 完整桌面視窗模式（pywebview）
python main.py

# 僅啟動 Flask，用瀏覽器開啟 http://127.0.0.1:5000 測試 UI
python app.py
```

---

## 🔐 預設管理員帳號

| 欄位 | 值 |
|------|----|
| 帳號 | `admin` |
| 密碼 | `admin123` |

> ⚠️ 建議於正式部署前修改預設密碼。

---

## 📊 資料匯入格式

匯入的 Excel / CSV 檔案需包含以下標頭欄位：

| 標頭名稱 | 說明 |
|----------|------|
| `編號` | 流水號，子編號格式如 `1.1`、`1.2` 將自動合併至主紀錄姓名欄 |
| `姓名` 或 `信眾姓名` | 點燈者姓名 |
| `金額` | 點燈金額（數字） |
| `壇名` | 所屬壇號 |

> 匯入為**累加模式**，執行後將新增至現有清單，不會刪除原有紀錄。

---

## 📦 一鍵打包為執行檔 (.exe)

雙擊 `build.bat` 即可自動完成打包，或手動執行：

```powershell
pyinstaller -F -w --clean ^
  --name "正坤點燈管理系統" ^
  --icon="favicon.ico" ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  main.py
```

打包完成後，執行檔位於 `dist/` 資料夾。

**交付說明：**
- 僅需提供 `正坤點燈管理系統.exe` 給使用者。
- 若需保留既有資料，請將 `temple_data.db` 放置於與 `.exe` 相同目錄下。

---

## 🔧 開發常用指令

```powershell
# 查看已安裝套件
pip list

# 更新 requirements.txt
pip freeze > requirements.txt
```

---

## 📋 API 端點一覽

| 方法 | 路徑 | 權限 | 說明 |
|------|------|------|------|
| `GET` | `/api/auth/status` | 公開 | 取得登入狀態 |
| `POST` | `/api/auth/login` | 公開 | 管理員登入 |
| `POST` | `/api/auth/logout` | 公開 | 登出並清除 Session |
| `GET` | `/api/records` | 公開 | 查詢紀錄（`?q=` 搜尋、`?all=true` 顯示全部） |
| `POST` | `/api/records` | 管理員 | 新增紀錄 |
| `PUT` | `/api/records/<id>` | 管理員 | 更新紀錄 |
| `DELETE` | `/api/records/<id>` | 管理員 | 刪除紀錄 |
| `POST` | `/api/records/import` | 管理員 | 累加匯入 CSV / XLSX |

---

## 📄 版本紀錄

| 版本 | 更新內容 |
|------|------|
| **v1.0.5** | 未登入時金額欄位自動模糊遮蔽 |
| v1.0.4 | 匯入改為累加模式；顯示全部限管理員可見；UI 改為台中市政府風格；登出後自動清除密碼欄；操作按鈕強制單行顯示 |
| v1.0.3 | 新增編輯功能；修正刪除後刷新邏輯；新增 CSV 匯入匯出 |

---

## 📄 授權

本專案為內部使用系統，僅供正坤宮廟管理用途。