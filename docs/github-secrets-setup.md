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

#### 生產環境 (production)

前往 **Settings** > **Environments** > **production** > **Environment secrets**

| Secret 名稱                 | 說明                                 | 範例值                                     |
| --------------------------- | ------------------------------------ | ------------------------------------------ |
| `VM_HOST`                   | 生產環境 GCP VM 的 IP 位址或主機名稱 | `34.80.234.56`                             |
| `DEPLOY_SSH_KEY`            | 生產環境部署用的 SSH 私鑰            | `-----BEGIN OPENSSH PRIVATE KEY-----\n...` |
| `POSTGRES_PASSWORD`         | PostgreSQL 資料庫密碼                | `prod_strong_password_2024`                |
| `ALLOW_MODIFY_API_KEY_LIST` | 允許修改資料的 API Keys（逗號分隔）  | `prod_key_1,prod_key_2,prod_key_3`         |

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

## 非敏感設定值

以下設定值不需要放在 Secrets 中，已直接寫在 `.github/workflows/cicd.yaml` 中：

- `ENVIRONMENT`：根據部署分支自動設定（dev/prod）
- `APP_TITLE`：固定為「花蓮光復救災平台 API」
- `PORT`：固定為 8080
- `POSTGRES_USER` / `DB_USER`：固定為 guangfu
- `POSTGRES_DB` / `DB_NAME`：固定為 guangfu
- `PROD_SERVER_URL`：固定為 https://api.gf250923.org
- `DEV_SERVER_URL`：固定為 https://uat-api.gf250923.org
- `DATABASE_URL`：自動組合（格式：`postgresql://{DB_USER}:{POSTGRES_PASSWORD}@postgres:5432/{DB_NAME}`）

如需修改這些值，請直接編輯 `.github/workflows/cicd.yaml` 檔案。

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

## 相關文件

- [GitHub Secrets 官方文件](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Environments 官方文件](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
