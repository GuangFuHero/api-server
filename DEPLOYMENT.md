# 部署文件

本文件說明如何將 GuanFu Backend 部署到 GCP Compute Engine。

## 部署架構

- **CI/CD**: GitHub Actions
- **容器化**: Docker + Docker Compose
- **連接方式**: SSH
- **觸發條件**:
  - 推送到 `develop` 分支 → 部署到開發環境 (dev)
  - 推送到 `main` 分支 → 部署到正式環境 (production)
  - 推送 Git tag（格式：`v*.*.*`）→ 部署特定版本到正式環境

## 前置準備

### 1. GCP VM 設定

在 GCP Compute Engine 上準備一台 VM，並完成以下設定：

```bash
# 創建 deploy 用戶
sudo adduser deploy
sudo usermod -aG docker deploy
sudo su - deploy

# 創建應用目錄
mkdir -p /home/deploy/api-server
cd /home/deploy/api-server

# 初次 clone repository
git clone https://github.com/GuangFuHero/api-server.git .

# 賦予 deploy.sh 執行權限
chmod +x deploy.sh
```

### 2. SSH 金鑰設定

```bash
# 在本機生成 SSH 金鑰對
ssh-keygen -t ed25519 -C "deploy@guangfu" -f ~/.ssh/guangfu_deploy

# 將公鑰加到 VM 的 deploy 用戶
# 在 VM 上執行：
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat ~/.ssh/guangfu_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. SSH 安全加固（建議）

為了增強安全性，設定 SSH 命令限制，只允許執行特定的部署相關命令：

```bash
# 在 VM 上的 deploy 用戶執行
# 創建日誌目錄
mkdir -p /home/deploy/logs

# 修改 ~/.ssh/authorized_keys，在公鑰前面加上命令限制
vim ~/.ssh/authorized_keys

# 在公鑰前面加上以下內容（整行）：
# command="/home/deploy/deploy-wrapper.sh",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-ed25519 AAAA...

# 完整範例：
# command="/home/deploy/deploy-wrapper.sh",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIxxx... deploy@guangfu
```

**說明：**

- `command="/home/deploy/deploy-wrapper.sh"` - 限制只能執行 wrapper 腳本
- `no-port-forwarding` - 禁止 port forwarding
- `no-X11-forwarding` - 禁止 X11 forwarding
- `no-agent-forwarding` - 禁止 agent forwarding

這樣設定後，所有透過此 SSH key 的連線都會被限制只能執行 `deploy-wrapper.sh` 允許的命令。

**注意：** CI/CD 會在每次部署時自動更新 `/home/deploy/deploy-wrapper.sh` 到最新版本，無需手動維護。

**查看部署日誌：**

```bash
# 在 VM 上查看部署日誌
tail -f /home/deploy/logs/deploy.log
```

### 4. GitHub Secrets 設定

在 GitHub Repository 的 Settings > Secrets and variables > Actions 中新增：

| Secret 名稱                  | 說明                       | 範例值                           |
| ---------------------------- | -------------------------- | -------------------------------- |
| `VM_HOST`                    | GCP VM 的 IP 位址          | `34.80.123.45`                   |
| `DEPLOY_SSH_KEY`             | deploy 用戶的私鑰          | 完整的私鑰內容（包含 BEGIN/END） |
| `POSTGRES_PASSWORD`          | PostgreSQL 資料庫密碼      | `your_strong_password_here`      |
| `ALLOW_MODIFY_API_KEY_LIST`  | 允許修改資料的 API Key 清單 | `key1,key2,key3`                 |

**注意：** CI/CD 會使用這些 secrets 自動生成 `.env` 檔案，無需在 VM 上手動設定環境變數。

### 5. 環境變數配置說明

CI/CD 會在每次部署時自動生成 `.env` 檔案，包含以下內容：

**開發環境 (develop 分支)：**
- `ENVIRONMENT=dev`
- `DEV_SERVER_URL=https://uat-api.gf250923.org`

**正式環境 (main 分支或 tag)：**
- `ENVIRONMENT=prod`
- `PROD_SERVER_URL=https://api.gf250923.org`

**共用設定：**
- 資料庫連線資訊（從 GitHub Secrets 自動組合）
- API Key（從 `ALLOW_MODIFY_API_KEY_LIST` secret）
- 應用程式標題：花蓮光復救災平台 API
- Port：8080

如需修改環境變數，請更新 GitHub Secrets 或修改 `guanfu_backend/setup-env.sh` 腳本。

### 6. 首次部署

首次部署建議使用 CI/CD 自動部署：

```bash
# 推送 main 分支觸發自動部署
git push origin main
```

或者在 VM 上手動執行首次部署：

```bash
cd /home/deploy/api-server

# 設定環境變數並執行部署（以正式環境為例）
export ENVIRONMENT=prod
export DB_PASS="your_postgres_password"
export API_KEY_LIST="key1,key2,key3"
./deploy.sh latest

# 首次部署後，檢查服務狀態
cd guanfu_backend
docker compose ps
docker compose logs -f backend

# 檢查 backend 是否正常運行
curl http://localhost:8000/docs
```

**注意：** 首次部署會自動初始化資料庫和啟動所有服務（postgres、backend、nginx）。

## 自動化部署流程

### 部署方式

#### 方式 1: 推送到 develop branch（部署到開發環境）

```bash
git push origin develop
```

這會自動執行 `./deploy.sh develop`，部署 develop 分支到開發環境 (dev)。

#### 方式 2: 推送到 main branch（部署最新版到正式環境）

```bash
git push origin main
```

這會自動執行 `./deploy.sh latest`，部署最新的 main 分支到正式環境 (production)。

#### 方式 3: 打 Git Tag（部署特定版本到正式環境）

```bash
# 創建並推送 tag（必須在 main 分支上）
git tag v1.0.0
git push origin v1.0.0
```

這會自動執行 `./deploy.sh v1.0.0`，部署指定的版本到正式環境 (production)。

**注意：** Tag 必須從 main 分支創建，否則部署會失敗。

### 部署流程

1. **觸發條件**

   - 推送到 `develop` 分支（開發環境）
   - 推送到 `main` 分支（正式環境）
   - 推送 tag（格式：`v*.*.*`，正式環境特定版本）

2. **GitHub Actions 自動執行**

   - 觸發 `.github/workflows/cicd.yaml`
   - 上傳 `deploy-wrapper.sh` 到 VM（更新安全規則）
   - SSH 連接到 GCP VM，並傳遞環境變數（DB_PASS、API_KEY_LIST 等）
   - 執行 `deploy.sh` 腳本：
     1. Git pull 最新代碼（包含 `setup-env.sh`）
     2. 自動執行 `setup-env.sh` 生成 `.env` 檔案
     3. 停止舊的 backend 容器
     4. 重新構建 backend 映像
     5. 啟動新的 backend 容器
   - **注意：** 只重啟 backend 容器（DB 和 nginx 保持運行）

3. **驗證部署**
   - 自動檢查 Docker 容器狀態
   - 自動檢查 backend 健康狀態（http://localhost:8000/docs）

### deploy.sh 功能說明

`deploy.sh` 腳本會執行以下操作：

1. 拉取指定版本的代碼：
   - `develop`: 拉取 develop 分支最新代碼
   - `latest`: 拉取 main 分支最新代碼
   - `v*.*.*`: 切換到指定 tag 版本
2. 自動生成 `.env` 檔案（如果提供了 `DB_PASS` 環境變數）
3. 停止舊的 backend 容器（**不停止 DB 和 nginx**）
4. 清理未使用的 Docker 映像
5. 重新構建 backend 映像
6. 啟動新的 backend 容器
7. 等待並驗證 backend 啟動成功（健康檢查）
8. 顯示最近的日誌

## 手動部署

如果需要手動部署，可以直接在 VM 上執行：

```bash
cd /home/deploy/api-server

# 部署 develop 分支（開發環境）
export ENVIRONMENT=dev
export DB_PASS="your_password"
export API_KEY_LIST="key1,key2,key3"
./deploy.sh develop

# 部署最新的 main 分支（正式環境）
export ENVIRONMENT=prod
export DB_PASS="your_password"
export API_KEY_LIST="key1,key2,key3"
./deploy.sh latest

# 部署指定版本（正式環境，需帶 v 前綴）
export ENVIRONMENT=prod
export DB_PASS="your_password"
export API_KEY_LIST="key1,key2,key3"
./deploy.sh v1.0.0
```

**注意：** 手動部署時需要設定環境變數，否則 `.env` 檔案不會自動生成。

## 監控與日誌

### 查看服務狀態

```bash
cd /home/deploy/api-server/guanfu_backend
docker compose ps
```

### 查看日誌

```bash
# Backend 日誌
docker compose logs -f backend

# 所有服務日誌
docker compose logs -f

# 最近 100 行日誌
docker compose logs --tail=100 backend
```

### 重啟服務

```bash
# 只重啟 backend
docker compose restart backend

# 重啟所有服務
docker compose restart
```

## 回滾部署

如果新版本有問題，可以快速回滾到舊版本：

### 方式 1: 使用 CI/CD 回滾

```bash
# 推送舊版本的 tag
git push origin v0.9.0
```

### 方式 2: 手動回滾

```bash
cd /home/deploy/api-server

# 設定環境變數
export ENVIRONMENT=prod
export DB_PASS="your_password"
export API_KEY_LIST="key1,key2,key3"

# 回滾到 v0.9.0
./deploy.sh v0.9.0
```

## Nginx 與 HTTPS 設定

如果需要配置 HTTPS（使用 Let's Encrypt）：

```bash
cd /home/deploy/api-server/guanfu_backend

# 首次申請憑證（如果 certbot/ 目錄已存在則跳過）
docker compose -f docker-compose-certbot.yaml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your@email.com \
  --agree-tos \
  --no-eff-email

# 重啟 nginx 套用憑證
docker compose restart nginx
```

## 環境變數生成機制

CI/CD 使用以下機制自動生成 `.env` 檔案：

1. **setup-env.sh 腳本**
   - 位於 `guanfu_backend/setup-env.sh`
   - 每次 git pull 後自動更新到最新版本
   - 由 `deploy.sh` 自動呼叫執行

2. **環境變數來源**
   - `ENVIRONMENT`: 根據分支自動判斷（develop → dev, main/tag → prod）
   - `DB_PASS`: 從 GitHub Secret `POSTGRES_PASSWORD` 傳入
   - `API_KEY_LIST`: 從 GitHub Secret `ALLOW_MODIFY_API_KEY_LIST` 傳入

3. **生成的 .env 檔案包含**
   - 應用程式設定（環境、標題、Port）
   - 資料庫連線資訊（自動組合 DATABASE_URL）
   - API Keys
   - 伺服器 URLs（dev/prod）

4. **如何修改環境變數**
   - **修改 Secrets**: 更新 GitHub Repository Secrets
   - **修改模板**: 編輯 `guanfu_backend/setup-env.sh` 並提交

## 故障排除

### .env 檔案未生成或為空

```bash
# 檢查環境變數是否正確傳入
cd /home/deploy/api-server/guanfu_backend
ls -la .env

# 手動執行 setup-env.sh 測試
export ENVIRONMENT=prod
export DB_PASS="your_password"
export API_KEY_LIST="key1,key2,key3"
./setup-env.sh

# 查看生成的 .env
cat .env
```

### Backend 無法啟動

```bash
# 檢查日誌
docker compose logs backend

# 檢查環境變數
docker compose config

# 重新構建
docker compose build --no-cache backend
docker compose up -d backend
```

### 資料庫連接失敗

```bash
# 檢查 postgres 是否運行
docker compose ps postgres

# 檢查 postgres 日誌
docker compose logs postgres

# 測試資料庫連接
docker compose exec postgres psql -U your_db_user -d guangfu_prod
```

### 磁碟空間不足

```bash
# 清理未使用的 Docker 資源
docker system prune -a --volumes

# 查看磁碟使用情況
df -h
docker system df
```

### SSH 命令被拒絕

```bash
# 在 VM 上查看 deploy-wrapper.sh 日誌
tail -f /home/deploy/logs/deploy.log

# 檢查 deploy-wrapper.sh 是否存在且可執行
ls -la /home/deploy/deploy-wrapper.sh

# 檢查 authorized_keys 設定
cat ~/.ssh/authorized_keys

# 如果需要重新設定 SSH 限制，參考「SSH 安全加固」章節
```

## 安全建議

1. **環境變數安全**

   - **不要**將 `.env` 檔案提交到 Git
   - 定期更換 `POSTGRES_PASSWORD`
   - 使用強密碼（至少 16 位，包含大小寫字母、數字、特殊符號）
   - 定期輪換 API Keys

2. **定期更新**

   - 定期更新 Docker 映像基底
   - 更新系統套件：`sudo apt update && sudo apt upgrade`
   - CI/CD 會自動更新 `deploy-wrapper.sh`，確保安全規則最新

3. **備份資料庫**

   ```bash
   # 備份
   docker compose exec postgres pg_dump -U your_db_user guangfu_prod > backup_$(date +%Y%m%d).sql

   # 還原
   docker compose exec -T postgres psql -U your_db_user guangfu_prod < backup_20241009.sql
   ```

4. **監控日誌**

   - 設定日誌輪轉，避免磁碟空間被日誌佔滿
   - 定期檢查異常訪問
   - 檢查 `/home/deploy/logs/deploy.log` 了解部署歷史

5. **防火牆設定**
   - 只開放必要的 port（80, 443, 22）
   - 限制 SSH 訪問來源 IP
   - 使用 SSH 命令限制（deploy-wrapper.sh）

## 相關文件

- [README.md](README.md) - 專案說明
- [guanfu_backend/README.md](guanfu_backend/README.md) - Backend 開發文件
- [table_spec.md](table_spec.md) - 資料庫規格
