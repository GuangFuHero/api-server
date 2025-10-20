## Tables

### places (站點列表)

| 欄位 | 類型 | 必填 | 說明 | 範例 |
|------|------|------|------|------|
| id | string | 是 | 資料庫唯一識別 ID | |
| name | string | 是 | 站點名稱 | |
| address | string | 是 | 完整地址（不能有空格、數字或英文一律半型） | 976台灣花蓮縣光復鄉忠孝路100號 |
| address_description | string | 否 | 針對地址的進一步說明 | 中正路跟佛祖街路口 |
| coordinates | jsonb | 是 | 經緯度 `{"type": "Point/Polygon/LineString", "coordinates": [[123.123, 24.123], [122.122, 23.122]]}` | |
| type | string | 是 | 站點類型：醫療/加水/廁所/洗澡/避難/住宿/物資/心理援助 | |
| sub_type | string | 否 | 站點服務類別 | 流動廁所/車站/學校/民宿/飯店 |
| info_sources | array | 否 | 資料來源連結陣列 | {"連結1", "連結2"} |
| verified_at | number | 否 | 資料最後被核實的時間 | |
| website_url | string | 否 | 單位官方連結 | |
| status | string | 是 | 站點狀態（嚴格限於：開放/暫停/關閉） | 開放 |
| resources | jsonb | 否 | 資源列表 `[{"name": "女廁", "count": 10, "unit": "座"}]` | |
| open_date | string | 否 | 站點開放日期 | 2025-09-30 |
| end_date | string | 否 | 站點預計關閉日期 | 2025-10-12 |
| open_time | string | 否 | 站點每天開放時間（24小時制，null 表示24小時開放） | 08:00:00 |
| end_time | string | 否 | 站點每天關閉時間（24小時制，null 表示24小時開放） | 20:00:00 |
| contact_name | string | 是 | 聯絡人 | 張先生 |
| contact_phone | string | 是 | 聯絡電話 | |
| notes | string | 否 | 其他備註 | |
| tags | jsonb | 否 | 標籤列表 `[{"priority": 1, "name": "標籤名"}]` | |
| created_at | number | 是 | 資料建立時間 | |
| updated_at | number | 是 | 最後更新時間 | |
| additional_info | jsonb | 否 | 其他可擴充欄位和值 | |


### requirements_hr (人力需求)

| 欄位 | 類型 | 必填 | 說明 | 範例 |
|------|------|------|------|------|
| id | string | 是 | 唯一識別 ID | |
| place_id | string | 是 | 關聯站點 ID（外鍵參照 places.id） | |
| required_type | string | 是 | 需求類型：一般志工/專業技術/清潔整理/醫療照護/後勤支援/其他 | 專業技術 |
| name | string | 是 | 需求名稱 | 水電工 |
| unit | string | 是 | 需求單位 | 人 |
| require_count | number | 是 | 需要數量 | 5 |
| received_count | number | 是 | 已支援數量 | 2 |
| tags | jsonb | 否 | 標籤列表 `[{"priority": 1, "name": "標籤名"}]` | |
| created_at | number | 是 | 資料建立時間 | |
| updated_at | number | 是 | 最後更新時間 | |
| additional_info | jsonb | 否 | 其他可擴充欄位和值 | |


### requirements_supplies (物資需求)

| 欄位 | 類型 | 必填 | 說明 | 範例 |
|------|------|------|------|------|
| id | string | 是 | 唯一識別 ID | |
| place_id | string | 是 | 關聯站點 ID（外鍵參照 places.id） | |
| required_type | string | 是 | 需求類型：飲食/醫療用品/生活用品等 | 飲食 |
| name | string | 是 | 需求名稱 | 箱水 |
| unit | string | 是 | 需求單位 | 箱 |
| require_count | number | 是 | 需要數量 | 100 |
| received_count | number | 是 | 已支援數量 | 50 |
| tags | jsonb | 否 | 標籤列表 `[{"priority": 1, "name": "標籤名"}]` | |
| created_at | number | 是 | 資料建立時間 | |
| updated_at | number | 是 | 最後更新時間 | |
| additional_info | jsonb | 否 | 其他可擴充欄位和值 | |

