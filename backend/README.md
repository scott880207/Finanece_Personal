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
