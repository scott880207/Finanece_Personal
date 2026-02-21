# 專案規格書 (Specification)

## 1. 專案概述
本專案為個人財務管理系統 (Personal Finance Management System)，旨在協助使用者追蹤資產、計算淨值、記錄交易損益，並透過視覺化儀表板掌握財務狀況。

## 2. 技術堆疊

### 2.1 後端 (Backend)
- **語言**: Python 3.9+
- **框架**: FastAPI
- **資料庫**: SQLite (透過 SQLAlchemy ORM)
- **排程**: APScheduler (每日淨值記錄)
- **其他**: Pydantic (資料驗證), Uvicorn (ASGI Server)

### 2.2 前端 (Frontend)
- **語言**: JavaScript / TypeScript
- **框架**: React 19
- **建置工具**: Vite
- **樣式**: Tailwind CSS
- **圖表**: Recharts
- **圖標**: Lucide React
- **HTTP Client**: Axios

## 3. 功能需求

### 3.1 資產管理 (Asset Management)
- **新增資產**: 記錄資產名稱、代碼、類別、數量、成本等。
- **查詢資產**: 列表顯示所有資產。
- **修改資產**: 更新資產資訊。
- **刪除資產**: 移除不再持有的資產。

### 3.2 淨值追蹤 (Net Worth Tracking)
- **即時淨值**: 根據當前資產計算總淨值 (TWD/USD)。
- **歷史淨值**: 每日自動記錄淨值快照。
- **淨值圖表**: 顯示淨值趨勢圖。支援X軸「近三個月」、「近一年」、「全部歷史走勢」三個時間區段切換 (預設近三個月)。

### 3.3 損益分析 (PnL Analysis)
- **已實現損益**: 記錄賣出資產後的損益。
- **累積損益**: 計算總體投資績效。

### 3.4 交易管理
- **未來交易**: 記錄預計發生的交易。
- **匯入交易**: 支援台股及美股 (US Broker) CSV 歷史交易資料自動匯入，並依先進先出法 (FIFO) 結算已實現損益。

## 4. 資料庫設計 (Schema)

本系統使用 SQLite，資料庫定義主要包含以下資料表：

### 4.1 資產表 (`assets`)
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

### 4.2 淨值歷史表 (`net_worth_history`)
記錄每日總淨值及資產快照。
- `id` (Integer): 主鍵
- `date` (Date): 記錄日期 (唯一)
- `total_twd` (Float): 台幣總淨值
- `total_usd` (Float): 美金總淨值
- `details` (JSON): 該日資產明細快照

### 4.3 已實現損益表 (`realized_pnl`)
記錄資產賣出或平倉後產生的損益。
- `id` (Integer): 主鍵
- `date` (Date): 實現日期
- `symbol` (String): 資產代碼
- `quantity` (Float): 交易數量
- `pnl` (Float): 損益金額
- `notes` (String): 備註說明

### 4.4 交易紀錄表 (`transactions`)
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

## 5. API 介面

- `POST /assets/`: 新增資產
- `GET /assets/`: 取得資產列表
- `PUT /assets/{id}`: 更新資產
- `DELETE /assets/{id}`: 刪除資產
- `GET /net-worth/current`: 取得當前淨值
- `GET /net-worth/history`: 取得淨值歷史
- `GET /pnl/history`: 取得損益歷史

## 6. 未來規劃
- 整合外部 API 取得即時股價。
- 多帳戶支援。
- 預算管理功能。
