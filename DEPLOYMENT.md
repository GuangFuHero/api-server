# 部署文件

本文件說明如何將 GuanFu Backend 部署到 GCP Compute Engine。

## 部署架構

- **CI/CD**: GitHub Actions
- **容器化**: Docker + Docker Compose
- **連接方式**: SSH
- **觸發條件**: 推送 Git tag（格式：`v*.*.*`）

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

### 3. SSH 安全加固（可選但建議）

為了增強安全性，可以設定 SSH 命令限制，只允許執行特定的部署相關命令：

```bash
# 在 VM 上的 deploy 用戶執行
cd /home/deploy

# 複製 deploy-wrapper.sh（從 repository）
cp api-server/deploy-wrapper.sh .
chmod +x deploy-wrapper.sh

# 創建日誌目錄
mkdir -p /home/deploy/logs

# 修改 ~/.ssh/authorized_keys，在公鑰前面加上命令限制
# 編輯 authorized_keys
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

**查看部署日誌：**

```bash
# 在 VM 上查看部署日誌
tail -f /home/deploy/logs/deploy.log
```

### 4. GitHub Secrets 設定

在 GitHub Repository 的 Settings > Secrets and variables > Actions 中新增：

| Secret 名稱      | 說明              | 範例值                           |
| ---------------- | ----------------- | -------------------------------- |
| `VM_HOST`        | GCP VM 的 IP 位址 | `34.80.123.45`                   |
| `DEPLOY_SSH_KEY` | deploy 用戶的私鑰 | 完整的私鑰內容（包含 BEGIN/END） |

### 5. 生產環境配置

在 GCP VM 上設定 `.env` 檔案：

```bash
cd /home/deploy/api-server/guanfu_backend
cp .env.example .env
vim .env
```

**必須修改的環境變數：**

```bash
# 應用程式設定
ENVIRONMENT=prod
APP_TITLE="花蓮光復救災平台 API"

# 資料庫設定
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_DB=guangfu_prod

```

### 6. 首次部署

在 VM 上手動執行首次部署：

```bash
cd /home/deploy/api-server/guanfu_backend

# 啟動所有服務（包含 DB 初始化）
docker compose up -d

# 檢查服務狀態
docker compose ps
docker compose logs -f backend

# 檢查 backend 是否正常運行
curl http://localhost:8000/docs
```

## 自動化部署流程

### 部署方式

#### 方式 1: 推送到 main branch（部署最新版）

```bash
git push origin main
```

這會自動執行 `./deploy.sh latest`，部署最新的 main branch 代碼。

#### 方式 2: 打 Git Tag（部署特定版本）

```bash
# 創建並推送 tag
git tag v1.0.0
git push origin v1.0.0
```

這會自動執行 `./deploy.sh v1.0.0`，部署指定的版本。

### 部署流程

1. **觸發條件**

   - 推送到 main branch，或
   - 推送 tag（格式：`v*.*.*`）

2. **GitHub Actions 自動執行**

   - 觸發 `.github/workflows/cicd.yaml`
   - SSH 連接到 GCP VM
   - 執行 `deploy.sh` 腳本
   - 只重啟 backend 容器（DB 和 nginx 保持運行）

3. **驗證部署**
   - 自動檢查 Docker 容器狀態
   - 自動檢查 backend 健康狀態

### deploy.sh 功能說明

`deploy.sh` 腳本會執行以下操作：

1. 拉取指定版本的代碼（tag 或 main branch）
2. 停止舊的 backend 容器（**不停止 DB 和 nginx**）
3. 清理未使用的 Docker 映像
4. 重新構建 backend 映像
5. 啟動新的 backend 容器
6. 等待並驗證 backend 啟動成功
7. 顯示最近的日誌

## 手動部署

如果需要手動部署，可以直接在 VM 上執行：

```bash
# 部署指定版本（需帶 v 前綴）
cd /home/deploy/api-server
./deploy.sh v1.0.0

# 部署最新的 main branch
./deploy.sh latest
```

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

```bash
cd /home/deploy/api-server
./deploy.sh v0.9.0  # 回滾到 v0.9.0
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

## 故障排除

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

## 安全建議

1. **定期更新**

   - 定期更新 Docker 映像基底
   - 更新系統套件：`sudo apt update && sudo apt upgrade`

2. **備份資料庫**

   ```bash
   # 備份
   docker compose exec postgres pg_dump -U your_db_user guangfu_prod > backup_$(date +%Y%m%d).sql

   # 還原
   docker compose exec -T postgres psql -U your_db_user guangfu_prod < backup_20241009.sql
   ```

3. **監控日誌**

   - 設定日誌輪轉，避免磁碟空間被日誌佔滿
   - 定期檢查異常訪問

4. **防火牆設定**
   - 只開放必要的 port（80, 443, 22）
   - 限制 SSH 訪問來源 IP

## 相關文件

- [README.md](README.md) - 專案說明
- [guanfu_backend/README.md](guanfu_backend/README.md) - Backend 開發文件
- [table_spec.md](table_spec.md) - 資料庫規格
