# 開發環境設定指南

本文件從零開始設定開發環境，即使沒有 Python 經驗也能快速啟動專案。

## 前置需求

- macOS 作業系統
- Homebrew（macOS 套件管理工具）
- Docker Desktop

## 快速開始

**零設定啟動** - 使用預設開發環境配置，適合立即開始開發：

```bash
# 1. 安裝 Docker Desktop（如果尚未安裝）
brew install --cask docker
# 啟動 Docker Desktop 應用程式

# 2. 進入專案目錄
cd guanfu_backend

# 3. 複製環境變數檔案（使用預設值）
cp .env.example .env.dev
# 編輯 .env.dev 填入資料庫設定

# 啟動資料庫與開發伺服器
docker-compose --env-file .env.dev up -d postgres
uvicorn src.main:app --reload
```

訪問 http://localhost:8080/docs 查看 API 文件。

# 4. 啟動所有服務
docker compose --env-file .env.dev up -d --build

# 5. 查看服務狀態
docker compose ps
```

訪問 <http://localhost:8080/docs> 查看 API 文件。

> **提示**：`.env.example` 已包含可直接使用的預設值，適合本地開發。
>
> **何時需要修改 `.env.dev`：**
>
> - 生產環境部署（請更換為強密碼）
> - 連接外部資料庫
> - 需要自訂應用程式設定

**停止服務：**

```bash
docker compose down        # 停止所有容器
docker compose down -v     # 停止並刪除資料（清空資料庫）
```

## 詳細安裝步驟

### 1. 安裝 Docker Desktop

```bash
brew install --cask docker
```

安裝後啟動 Docker Desktop 應用程式。

### 2. 設定環境變數

```bash
cd guanfu_backend
cp .env.example .env.dev
```

`.env.example` 已包含所有必要的設定和預設值，可直接使用。

**進階設定**（選用）：

如需自訂資料庫設定，可編輯 `.env.dev` 檔案：

```env
# PostgreSQL 容器設定
POSTGRES_USER=自訂使用者名稱
POSTGRES_PASSWORD=自訂密碼
POSTGRES_DB=資料庫名稱

# 後端應用程式資料庫設定（保持與上方一致）
DB_USER=自訂使用者名稱
DB_PASS=自訂密碼
DB_NAME=資料庫名稱

# 資料庫連線 URL（需同步更新）
DATABASE_URL=postgresql://自訂使用者名稱:自訂密碼@postgres:5432/資料庫名稱
```

**LINE 登入設定**（選用）：

如需啟用 LINE 登入功能，需在 `.env.dev` 中設定以下環境變數：

```env
# LINE 登入設定
LINE_CLIENT_ID=你的 LINE Channel ID
LINE_CLIENT_SECRET=你的 LINE Channel Secret
LINE_REDIRECT_URI=*/line/token
```

取得 LINE 登入憑證的步驟：
1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 或選擇現有的 Provider
3. 建立新的 LINE Login channel
4. 在 Channel 設定中取得 Channel ID 和 Channel Secret
5. 設定 Callback URL（例如：`http://localhost:8080/line/token`）

### 3. 啟動服務

```bash
# 建置並啟動所有服務
docker compose --env-file .env.dev up -d --build

# 查看服務狀態
docker compose ps

# 查看後端日誌
docker compose logs -f backend
```

### 4. 驗證服務

開啟瀏覽器訪問：

- API 文件：<http://localhost:8080/docs>
- 替代文件：<http://localhost:8080/redoc>

### 5. 常用操作

```bash
# 查看日誌
docker compose logs -f

# 重啟服務
docker compose restart

# 停止服務
docker compose down

# 停止並清除資料
docker compose down -v
```

伺服器啟動後，開啟瀏覽器訪問：

- API 文件：http://localhost:8080/docs
- 替代文件：http://localhost:8080/redoc

**優點：**
- 程式碼變更立即生效（hot reload）
- 可以使用 Python debugger
- 開發迭代速度快
- 只有資料庫在 Docker 中執行

如果需要使用 Python debugger 或 hot reload 功能，可以只用 Docker 執行資料庫，應用程式在本地執行。

### 1. 安裝 uv 套件管理工具

```bash
brew install uv
```

### 2. 設定 Python 環境

```bash
cd guanfu_backend
uv python install 3.13
uv sync
```

### 3. 修改 .env.dev 的資料庫連線

將 `.env.dev` 中的 `DATABASE_URL` 從 Docker 網路模式改為本地模式：

```env
# 註解掉 Docker 模式
# DATABASE_URL=postgresql://guangfu_user:guangfu_dev_pass_2024@postgres:5432/guangfu

# 啟用本地開發模式（使用 localhost）
DATABASE_URL=postgresql://guangfu_user:guangfu_dev_pass_2024@localhost:5432/guangfu
```

**關鍵差異：** 將 `@postgres:5432` 改為 `@localhost:5432`

### 4. 只啟動資料庫

```bash
docker compose --env-file .env.dev up -d postgres
```

### 5. 啟動開發伺服器

```bash
uv run uvicorn src.main:app --reload --port 8080
```

**優點：**

- 程式碼變更立即生效（hot reload）
- 可以使用 Python debugger
- 開發迭代速度快

## 常用指令參考

### Docker 服務管理

```bash
docker compose --env-file .env.dev up -d      # 啟動服務
docker compose down                            # 停止服務
docker compose logs -f backend                 # 查看後端日誌
docker compose restart                         # 重啟服務
```

### 本地開發（進階）

```bash
uv run uvicorn src.main:app --reload --port 8080   # 啟動開發伺服器
uv add <package-name>                              # 安裝新套件
uv sync                                            # 同步依賴
```

## 專案結構

```
guanfu_backend/
├── src/                    # 主要程式碼
│   ├── main.py            # FastAPI 入口
│   ├── models.py          # 資料庫模型
│   ├── schemas.py         # API 資料結構
│   ├── database.py        # 資料庫連線
│   └── routers/           # API 路由
├── docs/                  # 文件
├── uv.Dockerfile          # Docker 建構設定
├── docker-compose.yaml    # 服務編排設定
├── pyproject.toml         # 專案與套件設定
└── .env.dev               # 環境變數（不提交到 Git）
```

## 常見問題

### Docker 容器無法啟動？

檢查 5432 埠號是否被佔用：

```bash
lsof -i :5432
docker compose down -v
docker compose up -d
```

### 如何查看詳細錯誤訊息？

```bash
docker compose logs backend
docker compose logs postgres
```

### 資料庫連線失敗？

確認 `.env.dev` 中的資料庫設定是否正確，特別是 `POSTGRES_USER`、`POSTGRES_PASSWORD` 和 `POSTGRES_DB`。

### 需要使用 Python debugger？

參考「進階：本地開發模式」章節，使用本地開發方式可以直接使用 debugger。

## 相關資源

- [資料庫結構說明](../../table_spec.md)
- [FastAPI 官方文件](https://fastapi.tiangolo.com/zh/)
- [Docker Compose 文件](https://docs.docker.com/compose/)
