# Discord 通知整合使用指南

> 本指南說明如何在光復救災平台後端 API 中使用 Discord Webhook 發送通知

## 目錄

- [概述](#概述)
- [設置 Discord Webhook](#設置-discord-webhook)
- [環境配置](#環境配置)
- [使用方式](#使用方式)
- [API 測試範例](#api-測試範例)
- [注意事項](#注意事項)
- [疑難排解](#疑難排解)

---

## 概述

本專案已整合 Discord Webhook 通知功能，當有新的人力需求建立時，系統會自動發送通知到指定的 Discord 頻道。

**已整合的 Endpoint:**

- `POST /human_resources` - 建立新的人力需求時自動發送通知

**實現位置:**

- 通知服務：`src/services/discord_webhook.py`
- 整合範例：`src/routers/human_resources.py:90-93`

---

## 設置 Discord Webhook

### 步驟 1: 建立 Discord Webhook

1. 開啟 Discord 應用程式並進入目標伺服器
2. 點擊伺服器設定（齒輪圖示）
3. 選擇「整合」→「Webhooks」
4. 點擊「新增 Webhook」
5. 設定 Webhook 名稱（例如：光復救災通知）
6. 選擇要接收通知的頻道
7. 點擊「複製 Webhook URL」

**Webhook URL 格式範例：**

```
https://discordapp.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOP
```

### 步驟 2: 測試 Webhook（可選）

使用 curl 測試 Webhook 是否正常運作：

```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "測試訊息 - Discord Webhook 運作正常！"}'
```

---

## 環境配置

### 開發環境

在專案根目錄的 `.env` 或 `.env.dev` 檔案中添加：

```bash
# Discord Webhook
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

### 生產環境

確保在部署環境中設置環境變數：

```bash
export DISCORD_WEBHOOK_URL="https://discordapp.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

**Docker Compose 配置：**

在 `docker-compose.yaml` 中：

```yaml
services:
  backend:
    environment:
      DISCORD_WEBHOOK_URL: ${DISCORD_WEBHOOK_URL}
    env_file:
      - ./.env
```

---

## 使用方式

### 方法 1: 使用現有的通知服務

**基本用法：**

```python
from src.services.discord_webhook import send_discord_message

# 在 async 函數中使用
async def your_endpoint():
    # 發送簡單文字訊息
    await send_discord_message("測試訊息")
```

**帶有 JSON Embed 的訊息：**

```python
from src.services.discord_webhook import send_discord_message

async def your_endpoint():
    embed_data = {
        "org": "測試組織",
        "role_name": "志工",
        "headcount_need": 5,
        "status": "active"
    }

    await send_discord_message(
        content="新的志工需求已建立 ✨",
        embed_data=embed_data
    )
```

### 方法 2: 在背景發送（推薦）

使用 `asyncio.create_task()` 在背景發送通知，避免阻塞 API 回應：

```python
import asyncio
from src.services.discord_webhook import send_discord_message

@router.post("/your_endpoint")
async def create_something(data: YourSchema, db: Session = Depends(get_db)):
    # 處理業務邏輯
    result = crud.create_something(db, data)

    # 在背景發送通知（不等待完成）
    message_content = "新的資源已建立"
    embed_data = data.model_dump(mode='json')
    asyncio.create_task(
        send_discord_message(content=message_content, embed_data=embed_data)
    )

    return result
```

**優點：**

- ✅ 不阻塞 API 回應
- ✅ 提升使用者體驗
- ✅ 即使通知失敗也不影響主要業務邏輯

### 方法 3: 完整實作範例

參考 `src/routers/human_resources.py` 的實作：

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio

from .. import crud, models, schemas
from ..database import get_db
from ..services.discord_webhook import send_discord_message

router = APIRouter()

@router.post(
    "/human_resources",
    response_model=schemas.HumanResourceWithPin,
    status_code=201,
    summary="建立人力需求",
)
async def create_human_resource(
    resource_in: schemas.HumanResourceCreate,
    db: Session = Depends(get_db)
):
    """建立人力需求並發送 Discord 通知"""

    # 業務邏輯驗證
    if resource_in.headcount_got > resource_in.headcount_need:
        raise HTTPException(
            status_code=400,
            detail="headcount_got must be less than or equal to headcount_need."
        )

    # 創建資源
    created_resource = crud.create_with_input(
        db, models.HumanResource,
        obj_in=resource_in,
        valid_pin=generate_pin()
    )

    # 在背景發送 Discord 通知
    message_content = "新的志工人力需求已建立 ✨"
    embed_data = resource_in.model_dump(mode='json')
    asyncio.create_task(
        send_discord_message(content=message_content, embed_data=embed_data)
    )

    return created_resource
```

---

## API 測試範例

### 測試 POST /human_resources

**基本測試：**

```bash
curl -X POST http://localhost:8080/human_resources \
  -H "Content-Type: application/json" \
  -d '{
    "org": "測試組織",
    "address": "花蓮縣光復鄉測試路123號",
    "phone": "03-12345678",
    "status": "active",
    "role_name": "清潔志工",
    "role_type": "清潔/整理",
    "headcount_need": 5,
    "headcount_got": 2,
    "role_status": "pending",
    "has_medical": false,
    "skills": ["清潔", "整理"],
    "shift_notes": "早班 8:00-12:00"
  }'
```

**完整資料測試：**

```bash
curl -X POST http://localhost:8080/human_resources \
  -H "Content-Type: application/json" \
  -d '{
    "org": "測試志工組織ABC",
    "address": "花蓮縣光復鄉中正路一段100號",
    "phone": "03-87654321",
    "status": "active",
    "is_completed": false,
    "role_name": "醫療志工",
    "role_type": "一般志工",
    "headcount_need": 10,
    "headcount_got": 3,
    "role_status": "pending",
    "has_medical": true,
    "skills": ["急救", "護理"],
    "certifications": ["CPR證照", "護理師執照"],
    "experience_level": "level_1",
    "language_requirements": ["國語", "台語"],
    "headcount_unit": "人",
    "shift_notes": "需要有醫療背景，能配合夜班",
    "assignment_count": 5,
    "assignment_notes": "優先安排急診室支援"
  }'
```

**預期結果：**

- HTTP 狀態碼：`201 Created`
- API 回應包含創建的資源資料
- Discord 頻道收到新的通知訊息

---

## 注意事項

### ⚠️ 時間欄位處理

**重要：** 以下時間欄位**不需要在請求中傳入**，系統會自動填入當前 Unix timestamp：

- `shift_start_ts`
- `shift_end_ts`
- `assignment_timestamp`

**❌ 錯誤做法：**

```json
{
  "shift_start_ts": "2025-10-16T17:26:28.110Z",
  "shift_end_ts": "2025-10-16T17:26:28.110Z"
}
```

這會導致資料庫錯誤：`invalid input syntax for type bigint`

**✅ 正確做法：**

省略這些欄位，讓系統自動處理：

```json
{
  "org": "測試組織",
  "address": "花蓮縣光復鄉測試路123號",
  "phone": "03-12345678",
  "status": "active",
  "role_name": "志工",
  "role_type": "一般志工",
  "headcount_need": 10,
  "role_status": "pending"
}
```

### 📝 必填欄位清單

```yaml
org: 組織名稱 (string)
address: 地址 (string)
phone: 電話 (string)
status: 狀態 (enum: active/completed/cancelled)
role_name: 角色名稱 (string)
role_type: 角色類型 (enum: 一般志工/醫療照護/後勤支援/清潔/整理/專業技術/其他)
headcount_need: 需求人數 (integer, >= 0)
role_status: 角色狀態 (enum: completed/pending/partial)
```

### 🔍 可選欄位

```yaml
is_completed: 是否完成 (boolean, 預設: false)
headcount_got: 已獲得人數 (integer, 預設: 0)
has_medical: 是否需要醫療背景 (boolean)
skills: 所需技能 (array of strings)
certifications: 所需證照 (array of strings)
experience_level: 經驗等級 (enum: level_1/level_2/level_3, 預設: level_1)
language_requirements: 語言要求 (array of strings)
headcount_unit: 人數單位 (string)
shift_notes: 班別備註 (string)
assignment_count: 指派次數 (integer)
assignment_notes: 指派備註 (string)
```

### 🔐 安全性建議

1. **不要將 Webhook URL 提交到版控系統**

   - 將 `.env` 添加到 `.gitignore`
   - 使用環境變數管理敏感資訊

2. **定期輪換 Webhook**

   - 如果 URL 洩露，立即在 Discord 中重新生成

3. **限制訊息頻率**
   - 避免在短時間內發送大量訊息
   - Discord 有 rate limit 限制

---

## 疑難排解

### 問題 1: 訊息未發送到 Discord

**檢查清單：**

1. 確認環境變數已設置：

   ```bash
   # 在容器中檢查
   docker exec guanfu-backend printenv | grep DISCORD_WEBHOOK_URL
   ```

2. 驗證 Webhook URL 格式正確

3. 檢查 Discord 頻道權限

4. 查看應用程式日誌：

   ```bash
   docker logs guanfu-backend --tail 50 | grep -i discord
   ```

### 問題 2: 500 錯誤 - 時間欄位錯誤

**錯誤訊息：**

```
invalid input syntax for type bigint: "2025-10-16T17:26:28.110000Z"
```

**解決方案：**

- 不要在請求中傳入 `shift_start_ts`、`shift_end_ts`、`assignment_timestamp`
- 讓系統自動填入預設值

### 問題 3: 422 錯誤 - 驗證失敗

**常見原因：**

1. **缺少必填欄位**

   ```json
   { "address": ["Field required"] }
   ```

   解決：確保所有必填欄位都有提供

2. **錯誤的資料型別**

   ```json
   { "headcount_need": ["Input should be a valid integer"] }
   ```

   解決：檢查資料型別是否正確

3. **錯誤的 Enum 值**

   ```json
   { "status": ["Input should be 'active', 'completed' or 'cancelled'"] }
   ```

   解決：使用有效的 Enum 值

### 問題 4: 400 錯誤 - 業務邏輯驗證失敗

**錯誤訊息：**

```json
{ "detail": "headcount_got must be less than or equal to headcount_need." }
```

**解決方案：**

- 確保 `headcount_got` <= `headcount_need`

---

## 延伸閱讀

- [Discord Webhook 官方文件](https://discord.com/developers/docs/resources/webhook)
- [FastAPI 背景任務](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [專案 API 文件](http://localhost:8080/docs)（開發環境）

---

## 更新記錄

| 日期       | 版本  | 說明     |
| ---------- | ----- | -------- |
| 2025-10-17 | 1.0.0 | 初版發布 |

---

如有任何問題或建議，請在專案 GitHub 提出 Issue。
