# 後端服務 (Backend Service)

本目錄包含個人財務管理系統的後端程式碼，使用 Python 與 FastAPI 框架建置。

## 功能

- RESTful API 介面
- 資料庫模型與遷移 (SQLAlchemy)
- 排程任務 (APScheduler)
- 資料驗證 (Pydantic)

## 安裝與執行

### 1. 安裝相依套件

請確保已安裝 Python 3.9+，然後執行：

```bash
pip install -r requirements.txt
```

### 2. 資料庫設定

系統預設使用 SQLite 資料庫 (`finance.db`)，無需額外設定。資料庫檔案會自動生成於專案根目錄。

### 3. 啟動伺服器

```bash
# 請在專案根目錄執行
uvicorn backend.main:app --reload
```

## API 文件

伺服器啟動後，可由以下網址存取自動生成的 API 文件：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 專案結構

- `main.py`: 應用程式進入點
- `models.py`: 資料庫模型定義
- `schemas.py`: Pydantic 資料驗證模型
- `crud.py`: 資料庫操作邏輯
- `database.py`: 資料庫連線設定
- `services.py`: 業務邏輯 (如淨值計算)

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

