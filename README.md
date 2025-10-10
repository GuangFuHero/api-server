# 官網基本資訊

## 資訊總覽

| 資訊 | 內容 |
|------|------|
| Google Sheet 副本 | 光復救災平台用的副本 |
| 官網連結 | https://gf250923.org/map |
| 前端 UI Spec | https://www.figma.com/design/3HmmJtwok42obsXH93s21b/%E8%8A%B1%E8%93%AE%E5%85%89%E5%BE%A9%E5%BE%A9%E5%8E%9F%E4%B9%8B%E8%B7%AF%EF%BC%81?node-id=162-553&t=Fw2L65c6BsMguQRh-0 |
| 前端技術 | Google Site |
| 資料庫類型 | PostgreSQL |
| 資料庫資訊 (host/帳密) | https://github.com/PichuChen/guangfu250923 |
| 後端 API 框架 | Python FastAPI |
| 後端 API Spec | https://github.com/PichuChen/guangfu250923 |

## Alembic Migration 操作步驟

### 環境準備

1. 確保已安裝 Python 依賴套件
2. 設定好資料庫連線環境變數
3. 進入 `guanfu_backend` 目錄

### 基本 Migration 指令

#### 1. 檢查目前 Migration 狀態
```bash
cd guanfu_backend
alembic current
```

#### 2. 查看 Migration 歷史
```bash
alembic history --verbose
```

#### 3. 建立新的 Migration
```bash
# 自動偵測模型變更並產生 migration
alembic revision --autogenerate -m "描述變更內容"

# 手動建立空的 migration 檔案
alembic revision -m "描述變更內容"
```

#### 4. 執行 Migration
```bash
# 升級到最新版本
alembic upgrade head

# 升級到特定版本
alembic upgrade <revision_id>

# 升級一個版本
alembic upgrade +1
```

#### 5. 回滾 Migration
```bash
# 回滾到上一個版本
alembic downgrade -1

# 回滾到特定版本
alembic downgrade <revision_id>

# 回滾到初始狀態
alembic downgrade base
```

### 常用操作流程

#### 新增資料表或欄位
1. 修改 `src/models.py` 中的模型定義
2. 執行 `alembic revision --autogenerate -m "新增資料表/欄位"`
3. 檢查產生的 migration 檔案是否正確
4. 執行 `alembic upgrade head`

#### 修改現有欄位
1. 修改 `src/models.py` 中的模型定義
2. 執行 `alembic revision --autogenerate -m "修改欄位"`
3. 檢查並手動調整 migration 檔案（必要時）
4. 執行 `alembic upgrade head`

#### 刪除欄位或資料表
1. 修改 `src/models.py` 中的模型定義
2. 執行 `alembic revision --autogenerate -m "刪除欄位/資料表"`
3. 檢查產生的 migration 檔案
4. 執行 `alembic upgrade head`

### 注意事項

- 執行 migration 前務必備份資料庫
- 檢查自動產生的 migration 檔案，確保符合預期
- 在生產環境執行前，先在測試環境驗證
- 如需手動修改 migration 檔案，請謹慎處理
- 使用 `alembic show <revision_id>` 查看特定 migration 的詳細內容
