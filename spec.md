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
- **淨值圖表**: 顯示淨值趨勢圖。

### 3.3 損益分析 (PnL Analysis)
- **已實現損益**: 記錄賣出資產後的損益。
- **累積損益**: 計算總體投資績效。

### 3.4 交易管理
- **未來交易**: 記錄預計發生的交易。

## 4. 資料庫設計 (Schema)

### 4.1 Asset (資產)
- `id`: Integer, Primary Key
- `name`: String
- `category`: String
- ... (參照 `backend/models.py`)

### 4.2 NetWorthHistory (淨值歷史)
- `id`: Integer, Primary Key
- `date`: Date
- `total_twd`: Float
- `total_usd`: Float
- `details`: JSON (各資產明細)

### 4.3 RealizedPnL (已實現損益)
- `id`: Integer, Primary Key
- `date`: Date
- `amount`: Float
- ...

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
