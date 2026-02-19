# 個人財務管理系統 (Personal Finance Management System)

這是一個全端個人財務管理系統，使用 Python (FastAPI) 作為後端，React (Vite) 作為前端。

## 功能特色
- **資產追蹤**：管理各類資產（股票、現金、外幣等）。
- **淨值統計**：自動計算並記錄每日淨值趨勢。
- **損益分析**：追蹤已實現損益與累積績效。
- **視覺化儀表板**：透過圖表直觀了解財務狀況。

## 系統需求
- Python 3.9+
- Node.js 18+

## 安裝與執行

### 1. 後端設定 (Backend)

進入專案根目錄並安裝 Python 依賴套件：

```bash
pip install -r backend/requirements.txt
```

啟動後端伺服器：

```bash
# 在專案根目錄執行 (d:\Finanece_Personal)
uvicorn backend.main:app --reload
```

- API 文件: `http://localhost:8000/docs`

### 2. 前端設定 (Frontend)

進入前端目錄並安裝 Node.js 依賴套件：

```bash
cd frontend
npm install
```

啟動前端開發伺服器：

```bash
npm run dev
```

- 應用程式網址: `http://localhost:5173`

## 資料導入 (可選)

若有初始資料位於 `mydata/` 目錄，可執行以下腳本導入：

```bash
python import_data.py
```

## 疑難排解

### PowerShell 權限問題

若在執行 `npm run dev` 時遇到 `UnauthorizedAccess` 錯誤，請以管理員身分執行 PowerShell 並輸入：

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

或者使用 `npm.cmd`：

```bash
npm.cmd run dev
```
