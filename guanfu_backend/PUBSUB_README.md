# Request Logs PubSub 機制

## 概述

原本的同步 request logs 機制已經改為使用 Redis PubSub 的異步處理方式，以提高 API 回應效能並減少資料庫負載。

## 架構變更

### 原本的流程

```
HTTP Request → Middleware → 直接寫入資料庫 → HTTP Response
```

### 新的流程

```
HTTP Request → Middleware → Redis PubSub → 背景處理器 → 資料庫
                ↓
            HTTP Response (立即回應)
```

## 主要元件

### 1. PubSub 服務 (`src/pubsub.py`)

- 使用 Redis 作為訊息佇列
- 提供 `publish_request_log()` 方法發送請求日誌
- 提供 `subscribe_to_logs()` 方法訂閱訊息

### 2. 背景處理器 (`src/background_processor.py`)

- 訂閱 Redis PubSub 頻道
- 異步處理請求日誌並寫入資料庫
- 在應用程式啟動時自動啟動，關閉時自動停止

### 3. 修改的 Middleware (`src/main.py`)

- 移除了直接的資料庫寫入操作
- 改為發送訊息到 Redis PubSub
- 大幅提升 API 回應速度

## 設定需求

### 1. Redis 服務

需要運行 Redis 服務，可以通過 Docker Compose 啟動：

```bash
docker-compose up redis
```

### 2. 環境變數

確保 Redis 連接設定正確（預設為 localhost:6379）

## 部署步驟

### 1. 安裝依賴

```bash
uv sync
```

### 2. 啟動服務

```bash
# 啟動 Redis 和 PostgreSQL
docker-compose up -d postgres redis

# 啟動應用程式
uvicorn src.main:app --reload
```

### 3. 測試

```bash
# 執行測試腳本
python test_pubsub.py
```

## 優點

1. **效能提升**: API 回應不再被資料庫寫入操作阻塞
2. **可擴展性**: 可以輕鬆添加多個背景處理器
3. **容錯性**: 即使資料庫暫時不可用，請求日誌也不會丟失
4. **監控**: 可以監控 Redis 佇列狀態

## 監控

### 檢查 Redis 連接

```bash
redis-cli ping
```

### 監控 PubSub 頻道

```bash
redis-cli monitor
```

### 檢查佇列長度

```bash
redis-cli llen request_logs
```

## 故障排除

### 常見問題

1. **Redis 連接失敗**

   - 檢查 Redis 服務是否運行
   - 確認連接設定正確

2. **訊息未處理**

   - 檢查背景處理器是否正常啟動
   - 查看應用程式日誌

3. **資料庫寫入失敗**
   - 檢查資料庫連接
   - 查看背景處理器日誌

## 回滾方案

如果需要回滾到同步機制，可以：

1. 修改 `src/main.py` 中的 middleware
2. 移除 pubsub 相關的 import
3. 恢復原本的資料庫直接寫入邏輯
