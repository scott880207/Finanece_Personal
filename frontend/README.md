# 前端應用 (Frontend Application)

本目錄包含個人財務管理系統的前端程式碼，使用 React 與 Vite 建置。

## 技術堆疊

- React 19
- Vite
- Tailwind CSS
- Recharts (圖表)
- Lucide React (圖標)
- Axios (HTTP 請求)

## 安裝與執行

### 1. 安裝相依套件

請確保已安裝 Node.js 18+，然後執行：

```bash
npm install
```

### 2. 啟動開發伺服器

```bash
npm run dev
```

應用程式將於 locally 運行： `http://localhost:5173`

### 3. 建置生產版本

```bash
npm run build
```

## 專案結構

- `src/components`: UI 元件
- `src/App.jsx`: 主應用程式邏輯
- `src/main.jsx`: 進入點
- `tailwind.config.js`: Tailwind CSS 設定

## 資料庫結構 (Database Schema)

*供前端開發人員作為資料結構參考，請留意後端 API 返回的實際結構。*

本系統預設使用 SQLite，資料庫定義主要包含以下資料表：

### 1. 資產表 (`assets`)
記錄使用者當前持有的各項資產明細。
- `id` (Integer): 主鍵
- `type` (String): 資產類型 (例如: TWD, USD, TW_STOCK, US_STOCK 等)
- `symbol` (String): 資產代碼
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

