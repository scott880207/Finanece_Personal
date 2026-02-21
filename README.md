# 個人財務管理系統 (Personal Finance Management System)

這是一個全端個人財務管理系統，使用 Python (FastAPI) 作為後端，React (Vite) 作為前端。

## 功能特色
- **資產追蹤**：管理各類資產（股票、現金、外幣等）。
- **淨值統計**：自動計算並記錄每日淨值趨勢。圖表支援「近三個月」、「近一年」、「全部」時間區段檢視 (預設近三個月)。
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

若有初始資料位於 `mydata/` 目錄，可執行台股腳本導入：

```bash
python import_data.py
```

針對美股 (US Broker) 下載的 CSV 交易明細清單，可執行專屬擴充腳本 (含 FIFO 損益結算)：

```bash
python import_us.py
```


## 資料庫結構 (Database Schema)

本系統使用 SQLite，資料庫定義主要包含以下資料表：

### 1. 資產表 (`assets`)
記錄使用者當前持有的各項資產明細。
- `id` (Integer): 主鍵
- `type` (String): 資產類型 (例如: TWD, USD, TW_STOCK, US_STOCK 等)
- `symbol` (String): 資產代碼 (例如: 2330.TW, AAPL)
- `quantity` (Float): 持有數量
- `cost` (Float): 單位平均成本
- `currency` (String): 計價幣別 (預設 TWD)
- `leverage` (Float): 槓桿倍數 (預設 1.0)
- `contract_size` (Float): 合約規格 (預設 1.0)
- `margin` (Float): 保證金 (預設 0.0)
- `name` (String): 資產名稱
- `contract_month` (String): 合約月份 (適用於期貨，格式 YYYYMM)

### 2. 淨值歷史表 (`net_worth_history`)
記錄每日總淨值及資產快照。
- `id` (Integer): 主鍵
- `date` (Date): 記錄日期 (唯一)
- `total_twd` (Float): 台幣總淨值
- `total_usd` (Float): 美金總淨值
- `details` (JSON): 該日資產明細快照

### 3. 已實現損益表 (`realized_pnl`)
記錄資產賣出或平倉後產生的損益。
- `id` (Integer): 主鍵
- `date` (Date): 實現日期
- `symbol` (String): 資產代碼
- `quantity` (Float): 交易數量
- `pnl` (Float): 損益金額
- `notes` (String): 備註說明

### 4. 交易紀錄表 (`transactions`)
記錄每一筆買賣交易明細。
- `id` (Integer): 主鍵
- `date` (Date): 交易日期
- `asset_type` (String): 資產類型
- `symbol` (String): 資產代碼
- `action` (String): 交易動作 (BUY_OPEN, SELL_OPEN, SELL_CLOSE, BUY_CLOSE)
- `price` (Float): 成交價格
- `quantity` (Float): 成交數量
- `contract_month` (String): 合約月份
- `multiplier` (Float): 乘數 (預設 1.0)
- `fee` (Float): 手續費 (預設 0.0)
- `tax` (Float): 交易稅 (預設 0.0)
- `assigned_margin` (Float): 指派保證金 (預設 0.0)


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
