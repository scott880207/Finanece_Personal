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
