# 貢獻指南 (Contributing Guide)

歡迎參與花蓮光復救災平台後端系統的開發！這份文件將引導您了解如何為專案做出貢獻。

## 目錄

- [開發環境設定](#開發環境設定)
- [開發流程](#開發流程)
- [分支策略](#分支策略)
- [程式碼規範](#程式碼規範)
- [提交訊息規範](#提交訊息規範)
- [Pull Request 流程](#pull-request-流程)
- [測試指南](#測試指南)
- [資料庫 Migration](#資料庫-migration)
- [常見問題](#常見問題)

---

## 開發環境設定

### 前置需求

- Python 3.11 或以上版本
- Docker 和 Docker Compose
- Git

### 本地開發環境設定

1. **Clone 專案**

   ```bash
   git clone <repository-url>
   cd api-server
   ```

2. **建立 Python 虛擬環境**

/_TODO: change to uv or poetry_/

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

3. **安裝相依套件**

   ```bash
   cd guanfu_backend
   pip install -e .
   ```

4. **設定環境變數**

   ```bash
   # 複製環境變數範例檔案
   cp .env.example .env.dev
   # 編輯 .env.dev 填入必要的設定
   ```

5. **啟動資料庫**

   ```bash
   docker compose --env-file .env.dev up -d postgres
   ```

6. **啟動開發伺服器**

   ```bash
   uvicorn src.main:app --reload
   ```

7. **存取 API 文件**
   - 開啟瀏覽器前往：<http://localhost:8000/docs>

### Docker 部署模式

如果您想測試完整的容器化環境：

```bash
# 建置並啟動所有服務
docker compose --env-file .env.dev up -d --build

# 查看日誌
docker compose logs -f backend

# 停止服務
docker compose down
```

---

## 開發流程

### 分支策略

我們採用 Git Flow 分支策略：

```
main (生產環境)
  ↑
  PR + 審核
  ↑
develop (開發環境)
  ↑
  PR
  ↑
feature/* (功能開發)
hotfix/* (緊急修復)
```

### 分支說明

| 分支        | 用途     | 部署環境    | 保護規則                              |
| ----------- | -------- | ----------- | ------------------------------------- |
| `main`      | 生產版本 | Production  | 需要 PR review + CI 通過 + 審核者批准 |
| `develop`   | 開發整合 | Development | 需要 PR review + CI 通過              |
| `feature/*` | 功能開發 | 本地        | 無                                    |
| `hotfix/*`  | 緊急修復 | 本地        | 無                                    |

---

## 開發工作流程

### 1. 功能開發流程

```bash
# 1. 從 develop 創建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/add-new-api

# 2. 開發功能
# ... 編寫程式碼 ...

# 3. 執行本地測試
pytest  # 如果有測試的話
python -m ruff check .  # Lint 檢查

# 4. 提交變更
git add .
git commit -m "feat: add new API endpoint for shelter management"

# 5. 推送到遠端
git push origin feature/add-new-api

# 6. 在 GitHub 上建立 Pull Request
# - Base: develop
# - Compare: feature/add-new-api
# - 填寫 PR 描述（見下方 PR 模板）
# - 等待 CI 檢查通過
# - 等待 Code Review

# 7. PR 合併後，刪除功能分支
git branch -d feature/add-new-api
```

### 2. 發布到生產環境流程 (只允許 Admin 操作)

```bash
# 1. 確認 develop 分支穩定並測試完成

# 2. 建立 Release PR
# - Base: main
# - Compare: develop
# - 標題: "Release: v1.2.0"

# 3. PR 檢查通過後，等待審核者批准

# 4. 合併 PR 後自動部署到 Production

# 5. 建立 Git tag
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0

# 6. 同步 main 回 develop
git checkout develop
git merge main
git push origin develop
```

### 3. 緊急修復流程

```bash
# 1. 從 main 創建 hotfix 分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. 修復 bug
# ... 編寫修復程式碼 ...

# 3. 提交並推送
git add .
git commit -m "fix: resolve critical database connection issue"
git push origin hotfix/critical-bug

# 4. 建立 PR 到 main
# - Base: main
# - Compare: hotfix/critical-bug
# - 標記為緊急 (urgent label)

# 5. 快速 review 並合併

# 6. 將 hotfix 合併回 develop
git checkout develop
git merge hotfix/critical-bug
git push origin develop

# 7. 刪除 hotfix 分支
git branch -d hotfix/critical-bug
```

---

## 程式碼規範

### Python 程式碼風格

- 遵循 [PEP 8](https://pep8.org/) 規範
- 使用 [Ruff](https://github.com/astral-sh/ruff) 進行程式碼檢查
- 使用型別提示 (Type Hints)
- 函式和類別需要適當的 docstrings

### 專案結構規範

```
guanfu_backend/
├── src/
│   ├── routers/          # API 路由處理器
│   │   ├── shelters.py   # 避難所相關 API
│   │   └── ...
│   ├── main.py           # FastAPI 應用程式進入點
│   ├── models.py         # 資料庫模型
│   ├── schemas.py        # Pydantic schemas
│   ├── crud.py           # 資料庫操作
│   ├── database.py       # 資料庫連線
│   └── config.py         # 設定檔
├── tests/                # 測試檔案
├── Dockerfile            # Docker 建置檔
└── pyproject.toml        # 專案相依套件
```

### 命名規範

- **檔案名稱**: `snake_case.py`
- **類別名稱**: `PascalCase`
- **函式/變數名稱**: `snake_case`
- **常數名稱**: `UPPER_SNAKE_CASE`
- **私有成員**: `_leading_underscore`

### API 設計規範

- RESTful API 設計原則
- 使用適當的 HTTP 方法 (GET, POST, PUT, DELETE, PATCH)
- 統一的錯誤回應格式
- API 版本控制（如需要）

---

## 提交訊息規範

我們使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 類型

- `feat`: 新功能
- `fix`: bug 修復
- `docs`: 文件更新
- `style`: 格式調整（不影響程式碼運作）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 建置工具或輔助工具變動
- `perf`: 效能改善

### 範例

```bash
# 新增功能
git commit -m "feat(shelters): add filter by location API"

# 修復 bug
git commit -m "fix(database): resolve connection timeout issue"

# 文件更新
git commit -m "docs: update API documentation for supplies endpoint"

# 重構
git commit -m "refactor(crud): simplify database query logic"
```

### 提交訊息最佳實踐

- 使用現在式：「add feature」而非「added feature」
- 第一行不超過 50 字元
- 詳細說明寫在第二段（如需要）
- 引用相關的 issue：「fixes #123」或「refs #456」

---

## Pull Request 流程

### PR 描述模板

在建立 PR 時，請包含以下資訊：

```markdown
## 概述

<!-- 簡短描述這個 PR 的目的 -->

## 變更內容

<!-- 列出主要的程式碼變更 -->

- 新增了 XXX API endpoint
- 修改了 YYY 資料庫查詢邏輯
- 更新了 ZZZ 文件

## 測試方式

<!-- 說明如何測試這些變更 -->

1. 啟動開發伺服器
2. 前往 `/docs` 測試新的 API endpoint
3. 驗證回應格式是否正確

## 相關 Issue

<!-- 如果有相關的 issue，請連結 -->

Closes #123
Refs #456

## 截圖

<!-- 如果有 UI 變更，請提供截圖 -->

## Checklist

- [ ] 程式碼遵循專案規範
- [ ] 已新增/更新必要的測試
- [ ] 已更新相關文件
- [ ] CI 檢查全部通過
- [ ] 已在本地測試過
```

### Code Review 檢查清單

作為審核者，請檢查：

- [ ] 程式碼符合專案規範
- [ ] 有適當的錯誤處理
- [ ] 有必要的測試（如適用）
- [ ] 文件已更新（如需要）
- [ ] 沒有安全性問題
- [ ] 效能考量（如涉及資料庫查詢）
- [ ] API 設計合理
- [ ] 提交訊息符合規範

### PR 合併策略

- **功能分支 → develop**: Squash and merge（建議）
- **develop → main**: Create a merge commit
- **hotfix → main**: Create a merge commit

---

## 測試指南

### 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試檔案
pytest tests/test_shelters.py

# 執行測試並顯示覆蓋率
pytest --cov=src tests/
```

### 撰寫測試

- 每個新功能都應該有對應的測試
- 測試檔案放在 `tests/` 目錄
- 測試命名：`test_<feature_name>.py`
- 使用 pytest 框架

### 測試範例

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_get_shelters():
    response = client.get("/shelters")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_shelter():
    shelter_data = {
        "name": "測試避難所",
        "location": "花蓮縣光復鄉",
        "capacity": 100
    }
    response = client.post("/shelters", json=shelter_data)
    assert response.status_code == 201
```

---

## 資料庫 Migration

### 開發環境

```bash
# 啟動 PostgreSQL
docker compose --env-file .env.dev up -d postgres

# 執行 migration scripts
# (根據專案使用的 migration 工具而定)
```

### Migration 最佳實踐

1. **Migration 前確認**

   - [ ] Migration scripts 已提交到 repository
   - [ ] 在 dev 環境測試過
   - [ ] 準備好 rollback 計畫
   - [ ] 備份重要資料

2. **命名規範**

   - 檔案名稱包含時間戳記和描述
   - 範例：`20240101_add_shelter_capacity_column.sql`

3. **回滾計畫**
   - 每個 migration 都應該有對應的 rollback script
   - 測試回滾流程

---

## 環境變數管理

### 環境檔案

- **本地開發**: `.env.dev`（不要提交到 Git）
- **Dev 環境**: 使用 GitHub Secrets
- **Prod 環境**: 使用 GitHub Secrets + GCP Secret Manager

### 必要的環境變數

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=guanfu_db

# Application
ENVIRONMENT=dev
PORT=8000
```

---

## CI/CD Pipeline

### Workflow 概覽

| Workflow           | 觸發條件           | 執行內容                                |
| ------------------ | ------------------ | --------------------------------------- |
| **PR Check**       | PR to develop/main | Lint、測試、建置驗證                    |
| **Deploy to Dev**  | Push to develop    | 建置、推送 image、部署到 Dev            |
| **Deploy to Prod** | Push to main       | 建置、推送 image、部署到 Prod（需審核） |

### 本地執行 CI 檢查

在提交 PR 前，建議先在本地執行：

```bash
# Lint 檢查
ruff check .

# 格式化程式碼
ruff format .

# 執行測試
pytest

# 建置 Docker image 測試
docker build -t guanfu-backend:test -f guanfu_backend/Dockerfile guanfu_backend/
```

---

## 常見問題

### Q: 如何解決 merge conflict？

```bash
# 1. 更新本地 develop 分支
git checkout develop
git pull origin develop

# 2. 回到功能分支並 rebase
git checkout feature/your-feature
git rebase develop

# 3. 解決衝突後
git add .
git rebase --continue

# 4. 強制推送（因為 rebase 改變了歷史）
git push origin feature/your-feature --force-with-lease
```

### Q: 本地開發時資料庫連線失敗？

檢查：

1. Docker 容器是否正在執行：`docker ps`
2. `.env.dev` 設定是否正確
3. PostgreSQL 連線埠是否被佔用：`lsof -i :5432`

### Q: 如何更新相依套件？

```bash
# 更新特定套件
pip install --upgrade <package-name>

# 更新 pyproject.toml
# 手動編輯版本號碼

# 重新安裝
pip install -e .
```

### Q: PR 的 CI 檢查失敗怎麼辦？

1. 查看 GitHub Actions 的錯誤訊息
2. 在本地重現並修復問題
3. 提交修復並推送
4. CI 會自動重新執行

---

## 緊急回滾

如果生產環境出現問題，可以使用以下方式快速回滾：

### 方法 1: Revert commit

```bash
git revert <commit-hash>
git push origin main
```

### 方法 2: 部署舊版本 image

/_TODO: change to real env_/

```bash
# 使用 GCP Cloud Run
gcloud run deploy guanfu-backend-prod \
  --image asia-east1-docker.pkg.dev/.../guanfu-backend:prod-<old-sha>
```

### 方法 3: 回滾到之前的 tag

```bash
git checkout v1.1.0
# 觸發重新部署
```

---

## 取得協助

- 查看 [文件目錄](./guanfu_backend/docs/)
- 在 GitHub Issues 提出問題
- 聯繫專案維護者

---

## 授權

本專案用於救災協助目的。請確保您的貢獻符合專案的使用目的和道德準則。

---

感謝您對花蓮光復救災平台的貢獻！您的協助對社區非常重要。
