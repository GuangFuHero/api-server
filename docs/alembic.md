# 🔄 Alembic 資料庫遷移指南

> 使用 Alembic 管理資料庫結構變更

---

## 📋 目錄

- [環境準備](#-環境準備)
- [基本指令](#-基本-migration-指令)
- [常用操作流程](#-常用操作流程)
- [注意事項](#-注意事項)

---

## 🚀 環境準備

在開始使用 Alembic 之前，請確保：

- ✅ 已安裝 Python 依賴套件
- ✅ 設定好資料庫連線環境變數
- ✅ 進入 `guanfu_backend` 目錄

```bash
cd guanfu_backend
```

---

## 📖 基本 Migration 指令

### 1️⃣ 檢查目前 Migration 狀態

查看目前資料庫所在的 migration 版本：

```bash
alembic current
```

### 2️⃣ 查看 Migration 歷史

顯示所有 migration 的歷史記錄：

```bash
alembic history --verbose
```

### 3️⃣ 建立新的 Migration

#### 🤖 自動偵測模型變更

Alembic 會自動比對模型定義與資料庫結構，產生 migration 檔案：

```bash
alembic revision --autogenerate -m "描述變更內容"
```

#### ✏️ 手動建立空白 Migration

建立一個空的 migration 檔案，需要手動編寫遷移邏輯：

```bash
alembic revision -m "描述變更內容"
```

### 4️⃣ 執行 Migration

#### ⬆️ 升級到最新版本

```bash
alembic upgrade head
```

#### 🎯 升級到特定版本

```bash
alembic upgrade <revision_id>
```

#### ➕ 升級一個版本

```bash
alembic upgrade +1
```

### 5️⃣ 回滾 Migration

#### ⬇️ 回滾到上一個版本

```bash
alembic downgrade -1
```

#### 🎯 回滾到特定版本

```bash
alembic downgrade <revision_id>
```

#### 🔄 回滾到初始狀態

```bash
alembic downgrade base
```

### 6️⃣ 查看特定 Migration 詳細內容

```bash
alembic show <revision_id>
```

---

## 🛠️ 常用操作流程

### ➕ 新增資料表或欄位

1. 修改 `src/models.py` 中的模型定義
2. 執行自動偵測：
   ```bash
   alembic revision --autogenerate -m "新增資料表/欄位"
   ```
3. **檢查產生的 migration 檔案是否正確**
4. 執行遷移：
   ```bash
   alembic upgrade head
   ```

### ✏️ 修改現有欄位

1. 修改 `src/models.py` 中的模型定義
2. 執行自動偵測：
   ```bash
   alembic revision --autogenerate -m "修改欄位"
   ```
3. **檢查並手動調整 migration 檔案**（必要時）
4. 執行遷移：
   ```bash
   alembic upgrade head
   ```

### 🗑️ 刪除欄位或資料表

1. 修改 `src/models.py` 中的模型定義（移除相關程式碼）
2. 執行自動偵測：
   ```bash
   alembic revision --autogenerate -m "刪除欄位/資料表"
   ```
3. **檢查產生的 migration 檔案**
4. 執行遷移：
   ```bash
   alembic upgrade head
   ```

---

## ⚠️ 注意事項

### 🔒 安全性

- ⚠️ **執行 migration 前務必備份資料庫**
- ⚠️ 在生產環境執行前，先在測試環境驗證

### 📝 檔案檢查

- 📌 檢查自動產生的 migration 檔案，確保符合預期
- 📌 如需手動修改 migration 檔案，請謹慎處理
- 📌 autogenerate 不一定能偵測所有變更（如欄位重新命名）

### 🎯 最佳實踐

- 每次變更都應該建立一個新的 migration
- Migration 訊息應該清楚描述變更內容
- 不要修改已經執行過的 migration 檔案
- 定期清理過舊的 migration（在確保不會需要回滾的情況下）

---

## 📚 相關資源

- [Alembic 官方文件](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 文件](https://docs.sqlalchemy.org/)
- [API 規格文件](../table_spec.md)

---

[⬅️ 返回主頁](../README.md)
