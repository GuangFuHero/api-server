<div align="center">

# 🏔️ 花蓮光復救災平台 API Server

### 復原之路，科技相助 🤝

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Alembic](https://img.shields.io/badge/Alembic-6BA81E?style=for-the-badge&logo=python&logoColor=white)](https://alembic.sqlalchemy.org/)

[🌐 官網](https://gf250923.org/map) • [📚 API 文件](https://github.com/GuangFuHero/api-server/blob/main/table_spec.md) • [🎨 UI 設計](https://www.figma.com/design/3HmmJtwok42obsXH93s21b/%E8%8A%B1%E8%93%AE%E5%85%89%E5%BE%A9%E5%BE%A9%E5%8E%9F%E4%B9%8B%E8%B7%AF%EF%BC%81?node-id=162-553&t=Fw2L65c6BsMguQRh-0)

</div>

---

## 📋 目錄

- [專案資訊](#-專案資訊)
- [技術架構](#-技術架構)
- [快速開始](#-快速開始)
- [開發文件](#-開發文件)

---

## 📌 專案資訊

> 提供花蓮光復地區救災相關資訊的後端 API 服務

### 🔗 重要連結

| 項目 | 說明          |                                                                                        連結                                                                                         |
| :--: | :------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|  🌐  | **官網**      |                                                                      [gf250923.org](https://gf250923.org/map)                                                                       |
|  🎨  | **UI 設計稿** | [Figma](https://www.figma.com/design/3HmmJtwok42obsXH93s21b/%E8%8A%B1%E8%93%AE%E5%85%89%E5%BE%A9%E5%BE%A9%E5%8E%9F%E4%B9%8B%E8%B7%AF%EF%BC%81?node-id=162-553&t=Fw2L65c6BsMguQRh-0) |
|  📚  | **API 規格**  |                                                 [table_spec.md](https://github.com/GuangFuHero/api-server/blob/main/table_spec.md)                                                  |
|  📊  | **資料來源**  |                                                                                  Google Sheet 副本                                                                                  |

---

## 🛠️ 技術架構

<div align="center">

|    技術層    | 使用技術         |
| :----------: | :--------------- |
|   **前端**   | Google Site      |
|   **後端**   | Python + FastAPI |
|  **資料庫**  | PostgreSQL       |
|   **ORM**    | SQLAlchemy       |
| **遷移工具** | Alembic          |

</div>

---

## 🚀 快速開始

### Docker 方式（推薦）

```bash
cd guanfu_backend

# 1. 複製環境變數檔案
cp .env.example .env.dev

# 2. 啟動所有服務（資料庫 + 後端）
docker compose --env-file .env.dev up -d --build

# 3. 查看 API 文件
# 訪問 http://localhost:8080/docs
```

### 本地開發方式

```bash
cd guanfu_backend

# 1. 安裝 uv 套件管理工具
brew install uv

# 2. 設定 Python 環境
uv python install 3.13
uv sync

# 3. 只啟動資料庫
docker compose --env-file .env.dev up -d postgres

# 4. 啟動開發伺服器
uv run uvicorn src.main:app --reload --port 8080
```

> 📖 **詳細說明請參考**：[開發環境設定指南](guanfu_backend/docs/getting-started.md)

---

## 📚 開發文件

| 文件                                                      | 說明                                      |
| :-------------------------------------------------------- | :---------------------------------------- |
| 🚀 [開發環境設定](guanfu_backend/docs/getting-started.md) | 從零開始設定開發環境（Docker / 本地開發） |
| 🔄 [Alembic 遷移指南](docs/alembic.md)                    | 資料庫結構變更與遷移操作                  |
| 📊 [API 規格](table_spec.md)                              | 完整的 API 端點與資料表規格               |
| 🔀 [Git Flow 圖示](docs/git-flow-diagram.md)              | 專案的 Git 工作流程                       |
| 🖥️ [部署指南](DEPLOYMENT.md)                              | 部署到 Compute Engine 的步驟              |
| 🤝 [貢獻指南](CONTRIBUTING.md)                            | 如何參與專案開發                          |

---

## 🙏 致謝

感謝所有參與花蓮光復救災工作的志工與開發者們！

---

<div align="center">

Made with ❤️ for 花蓮光復

</div>
