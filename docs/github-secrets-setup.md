# GitHub Secrets 設定指南

本文件說明如何在 GitHub 中設定 CI/CD 所需的 Secrets。

## 前置作業

1. 前往你的 GitHub repository
2. 點選 **Settings** > **Environments**
3. 確認已建立 `dev` 和 `production` 兩個環境
4. 分別在每個環境中設定對應的 secrets

## 必要的 Secrets 設定

所有 secrets 都需要分別在 **dev** 和 **production** 環境中設定，因為開發和生產環境使用不同的伺服器和設定值。

### Environment Secrets（依環境設定）

這些 secrets 需要分別在 **dev** 和 **production** 環境中設定：

#### 開發環境 (dev)

前往 **Settings** > **Environments** > **dev** > **Environment secrets**

| Secret 名稱                 | 說明                                 | 範例值                                     |
| --------------------------- | ------------------------------------ | ------------------------------------------ |
| `VM_HOST`                   | 開發環境 GCP VM 的 IP 位址或主機名稱 | `35.201.123.45`                            |
| `DEPLOY_SSH_KEY`            | 開發環境部署用的 SSH 私鑰            | `-----BEGIN OPENSSH PRIVATE KEY-----\n...` |
| `POSTGRES_PASSWORD`         | PostgreSQL 資料庫密碼                | `dev_db_password_2024`                     |
| `ALLOW_MODIFY_API_KEY_LIST` | 允許修改資料的 API Keys（逗號分隔）  | `dev_key_1,dev_key_2`                      |
| `LINE_CLIENT_ID`            | LINE Login Channel ID（開發環境）    | `1234567890`                               |
| `LINE_CLIENT_SECRET`        | LINE Login Channel Secret（開發環境）| `abcdef1234567890abcdef1234567890`         |

#### 生產環境 (production)

前往 **Settings** > **Environments** > **production** > **Environment secrets**

| Secret 名稱                 | 說明                                 | 範例值                                     |
| --------------------------- | ------------------------------------ | ------------------------------------------ |
| `VM_HOST`                   | 生產環境 GCP VM 的 IP 位址或主機名稱 | `34.80.234.56`                             |
| `DEPLOY_SSH_KEY`            | 生產環境部署用的 SSH 私鑰            | `-----BEGIN OPENSSH PRIVATE KEY-----\n...` |
| `POSTGRES_PASSWORD`         | PostgreSQL 資料庫密碼                | `prod_strong_password_2024`                |
| `ALLOW_MODIFY_API_KEY_LIST` | 允許修改資料的 API Keys（逗號分隔）  | `prod_key_1,prod_key_2,prod_key_3`         |
| `LINE_CLIENT_ID`            | LINE Login Channel ID（生產環境）    | `9876543210`                               |
| `LINE_CLIENT_SECRET`        | LINE Login Channel Secret（生產環境）| `fedcba0987654321fedcba0987654321`         |

## 設定步驟

### Environment Secrets 設定

#### 建立環境（如果尚未建立）

1. 前往 **Settings** > **Environments**
2. 點選 **New environment**
3. 輸入環境名稱：`dev` 或 `production`
4. 點選 **Configure environment**

#### 新增 Environment Secrets

1. 在環境設定頁面，找到 **Environment secrets** 區塊
2. 點選 **Add secret**
3. 輸入 **Name** 和 **Value**
4. 點選 **Add secret**
5. 重複以上步驟直到所有 secrets 都設定完成

## 取得 SSH 私鑰

建議為開發和生產環境分別產生不同的 SSH 金鑰，以提高安全性。

### 產生開發環境金鑰

```bash
# 產生開發環境 SSH 金鑰對
ssh-keygen -t ed25519 -C "deploy@guangfu-dev" -f ~/.ssh/guangfu_deploy_dev

# 查看私鑰內容（放到 dev 環境的 DEPLOY_SSH_KEY）
cat ~/.ssh/guangfu_deploy_dev

# 查看公鑰內容（放到開發環境 GCP VM）
cat ~/.ssh/guangfu_deploy_dev.pub
```

### 產生生產環境金鑰

```bash
# 產生生產環境 SSH 金鑰對
ssh-keygen -t ed25519 -C "deploy@guangfu-prod" -f ~/.ssh/guangfu_deploy_prod

# 查看私鑰內容（放到 production 環境的 DEPLOY_SSH_KEY）
cat ~/.ssh/guangfu_deploy_prod

# 查看公鑰內容（放到生產環境 GCP VM）
cat ~/.ssh/guangfu_deploy_prod.pub
```

### 在 GCP VM 上設定公鑰

**開發環境 VM：**

1. SSH 登入到開發環境 GCP VM
2. 切換到 deploy 使用者：`sudo su - deploy`
3. 編輯 authorized_keys：`nano ~/.ssh/authorized_keys`
4. 將開發環境公鑰內容貼上並儲存

**生產環境 VM：**

1. SSH 登入到生產環境 GCP VM
2. 切換到 deploy 使用者：`sudo su - deploy`
3. 編輯 authorized_keys：`nano ~/.ssh/authorized_keys`
4. 將生產環境公鑰內容貼上並儲存

## 取得 LINE Login 憑證

建議為開發和生產環境分別建立不同的 LINE Login channel，以便獨立管理和測試。

### 建立 LINE Login Channel

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 使用 LINE 帳號登入
3. 如果沒有 Provider，點選 **Create** 建立新的 Provider
   - Provider name：例如「花蓮光復救災平台」
4. 在 Provider 頁面點選 **Create a LINE Login channel**

### 開發環境設定

1. 建立開發環境 channel：
   - Channel name：例如「光復救災平台 - Dev」
   - Channel description：開發環境用途說明
   - App types：Web app
2. 在 **Basic settings** 頁籤：
   - 複製 **Channel ID** → 設定到 GitHub Secrets 的 `LINE_CLIENT_ID`（dev 環境）
   - 複製 **Channel secret** → 設定到 GitHub Secrets 的 `LINE_CLIENT_SECRET`（dev 環境）
3. 在 **LINE Login** 頁籤：
   - Callback URL：新增 `https://uat-api.gf250923.org/line/callback`

### 生產環境設定

1. 建立生產環境 channel（重複上述步驟）：
   - Channel name：例如「光復救災平台 - Production」
   - Channel description：生產環境用途說明
   - App types：Web app
2. 在 **Basic settings** 頁籤：
   - 複製 **Channel ID** → 設定到 GitHub Secrets 的 `LINE_CLIENT_ID`（production 環境）
   - 複製 **Channel secret** → 設定到 GitHub Secrets 的 `LINE_CLIENT_SECRET`（production 環境）
3. 在 **LINE Login** 頁籤：
   - Callback URL：新增 `https://api.gf250923.org/line/callback`

### 重要提醒

- **Channel secret 只會顯示一次**，請務必妥善保存
- 如果遺失 Channel secret，需要在 LINE Developers Console 重新發行
- Callback URL 必須與 `setup-env.sh` 自動生成的 `LINE_REDIRECT_URI` 完全一致

## 非敏感設定值

以下設定值不需要放在 Secrets 中，已直接寫在 `.github/workflows/cicd.yaml` 或 `setup-env.sh` 中：

- `ENVIRONMENT`：根據部署分支自動設定（dev/prod）
- `APP_TITLE`：固定為「花蓮光復救災平台 API」
- `PORT`：固定為 8080
- `POSTGRES_USER` / `DB_USER`：固定為 guangfu
- `POSTGRES_DB` / `DB_NAME`：固定為 guangfu
- `PROD_SERVER_URL`：固定為 https://api.gf250923.org
- `DEV_SERVER_URL`：固定為 https://uat-api.gf250923.org
- `DATABASE_URL`：自動組合（格式：`postgresql://{DB_USER}:{POSTGRES_PASSWORD}@postgres:5432/{DB_NAME}`）
- `LINE_REDIRECT_URI`：根據環境自動生成
  - 生產環境：`https://api.gf250923.org/line/callback`
  - 開發環境：`https://uat-api.gf250923.org/line/callback`

如需修改這些值，請直接編輯 `.github/workflows/cicd.yaml` 或 `setup-env.sh` 檔案。

### 為什麼 DATABASE_URL 不需要設定為 Secret？

`DATABASE_URL` 會在部署時自動組合，格式為：
```
postgresql://{DB_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
```

其中：
- `DB_USER`、`DB_HOST`、`DB_PORT`、`DB_NAME` 都是固定值
- 只有 `POSTGRES_PASSWORD` 從 GitHub Secret 取得

這樣的好處是：
1. **更容易維護**：修改資料庫設定（如 host、port）不需要更新 secret
2. **更安全**：只需保密密碼，其他資訊可以透明化
3. **更靈活**：可以在 workflow 中輕鬆調整連線參數

## 驗證設定

設定完成後，可以透過以下方式驗證：

1. 推送代碼到 `develop` 或 `main` 分支
2. 前往 **Actions** 頁面查看 workflow 執行狀況
3. 如果設定正確，workflow 應該會成功執行並部署到對應環境

## 安全性注意事項

1. **絕對不要**將 secrets 提交到 Git repository 中
2. **定期更換**資料庫密碼和 API keys
3. **使用強密碼**：至少 16 個字元，包含大小寫字母、數字和特殊符號
4. **限制存取權限**：只給需要的人員 repository 的管理權限
5. **監控 secrets 使用**：定期檢查 Actions logs，確保沒有異常活動

## 疑難排解

### 問題：workflow 顯示 "Secret not found"

**解決方法：**

1. 確認 secret 名稱拼寫正確（區分大小寫）
2. 確認 secret 已設定在正確的位置（repository secrets 或 environment secrets）
3. 確認環境名稱正確（dev 或 production）

### 問題：SSH 連線失敗

**解決方法：**

1. 確認 `VM_HOST` 設定正確
2. 確認 `DEPLOY_SSH_KEY` 包含完整的私鑰內容（包括開頭和結尾）
3. 確認公鑰已正確設定在 GCP VM 上
4. 確認 GCP VM 的防火牆規則允許 SSH 連線（port 22）

### 問題：資料庫連線失敗

**解決方法：**

1. 確認 `POSTGRES_PASSWORD` 設定正確
2. 檢查部署日誌，確認 DATABASE_URL 組合正確
3. 確認資料庫容器正在運行：`docker compose ps`
4. 檢查資料庫 logs：`docker compose logs postgres`
5. 確認資料庫 host (`postgres`) 在 Docker 網路中可連線

### 問題：LINE Login 無法使用

**解決方法：**

1. 確認 `LINE_CLIENT_ID` 和 `LINE_CLIENT_SECRET` 設定正確
2. 檢查 LINE Developers Console 中的 Callback URL 是否正確：
   - 開發環境：`https://uat-api.gf250923.org/line/callback`
   - 生產環境：`https://api.gf250923.org/line/callback`
3. 確認 LINE Login channel 狀態為「Published」
4. 檢查應用程式日誌中是否有 LINE API 相關錯誤訊息
5. 驗證 `LINE_REDIRECT_URI` 環境變數是否正確生成：
   - 在 VM 上執行：`docker compose exec backend env | grep LINE`

## 相關文件

- [GitHub Secrets 官方文件](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Environments 官方文件](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [LINE Login 官方文件](https://developers.line.biz/en/docs/line-login/)
- [LINE Developers Console](https://developers.line.biz/)
