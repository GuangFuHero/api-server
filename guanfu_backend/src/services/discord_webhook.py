import httpx
from ..config import settings
import json
from datetime import datetime
from typing import Optional


def format_human_resource_notification(
    resource_data: dict,
    resource_id: str,
    created_at,
    client_ip: str,
    user_agent: str,
) -> str:
    """
    格式化人力需求通知訊息

    Args:
        resource_data: 人力需求資料
        resource_id: 資料庫 ID
        created_at: 建立時間 (datetime 對象或 UNIX timestamp)
        client_ip: 客戶端 IP
        user_agent: 使用者代理字串
    """
    # 如果是 UNIX timestamp，轉換為 datetime
    if isinstance(created_at, int) or isinstance(created_at, float):
        from datetime import datetime as dt_class, timezone
        created_at = dt_class.fromtimestamp(created_at, tz=timezone.utc)

    # 格式化時間為台灣格式
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekdays[created_at.weekday()]
    time_str = f"{weekday}, {created_at.strftime('%B %d, %Y %p %I:%M').replace('AM', '上午').replace('PM', '下午')}"

    # 構建訊息
    role_type = resource_data.get("role_type", "未指定")
    role_status = resource_data.get("role_status", "")
    type_display = f"{role_type} / {role_status}" if role_status else role_type

    headcount = resource_data.get("headcount_need", 0)
    unit = resource_data.get("headcount_unit", "人")

    notes_parts = []
    if resource_data.get("shift_notes"):
        notes_parts.append(resource_data["shift_notes"])
    if resource_data.get("assignment_notes"):
        notes_parts.append(resource_data["assignment_notes"])
    notes = "\n".join(notes_parts) if notes_parts else "無"

    message = f"""有人新增人力需求了 (開單) 🛠️
標題: {resource_data.get('role_name', '未命名')}
需求類型: {type_display}
需求人數: {headcount} {unit}
備註: {notes}
發出時間: {time_str}
資料庫ID: {resource_id}
IP: {client_ip}
User-Agent: {user_agent}"""

    return message


def format_supply_notification(
    supply_data: dict,
    supply_id: str,
    created_at,
    client_ip: str,
    user_agent: str,
) -> str:
    """
    格式化物資需求通知訊息

    Args:
        supply_data: 物資需求資料
        supply_id: 資料庫 ID
        created_at: 建立時間 (datetime 對象或 UNIX timestamp)
        client_ip: 客戶端 IP
        user_agent: 使用者代理字串
    """
    # 構建物資項目資訊
    supplies_dict = supply_data.get("supplies", {})
    item_str = ""

    if isinstance(supplies_dict, dict):
        # 取得物資名稱和數量
        item_name = supplies_dict.get("name", "未知物資")
        total_number = supplies_dict.get("total_number", 0)
        item_str = f"{item_name} x{total_number}"

    name = supply_data.get("name", "")
    phone = supply_data.get("phone", "")
    address = supply_data.get("address", "")
    notes = supply_data.get("notes", "")

    message = f"""物資需求出現了 🐝
Name: {name}
ID: {supply_id}
Phone: {phone}
Address: {address}
Item: {item_str}
Notes: {notes}
IP: {client_ip} (TW)
User-Agent: {user_agent}"""

    return message


def format_human_resource_patch_notification(
    resource_id: str,
    resource_data: dict,
    client_ip: str,
    user_agent: str,
) -> str:
    """
    格式化人力需求更新通知訊息

    Args:
        resource_id: 資料庫 ID
        resource_data: 完整的資源資料（包含 role_name, headcount_got, headcount_need 等）
        client_ip: 客戶端 IP
        user_agent: 使用者代理字串
    """
    role_name = resource_data.get("role_name", "未命名")
    headcount_got = resource_data.get("headcount_got", 0)
    headcount_need = resource_data.get("headcount_need", 0)
    unit = resource_data.get("headcount_unit") or "人"

    message = f"""有人報名人力需求了 (報名) 👷🏻
標題: {role_name} ({resource_id})
報名/需求人數: {headcount_got}/{headcount_need} {unit}
IP: {client_ip} (TW)
User-Agent: {user_agent}"""

    return message


def format_supply_patch_notification(
    supply_id: str,
    updated_fields: dict,
    client_ip: str,
    user_agent: str,
) -> str:
    """
    格式化物資需求更新通知訊息

    Args:
        supply_id: 資料庫 ID
        updated_fields: 更新的欄位
        client_ip: 客戶端 IP
        user_agent: 使用者代理字串
    """
    # 構建更新欄位列表
    fields_str = "\n".join([f"  - {key}: {value}" for key, value in updated_fields.items() if value is not None])

    message = f"""有人更新物資需求了 (改單) ✏️
資料庫ID: {supply_id}
更新欄位:
{fields_str}
IP: {client_ip} (TW)
User-Agent: {user_agent}"""

    return message


async def send_discord_message(content: str, embed_data: dict | None = None):
    """
    Sends a message to a Discord webhook.

    Args:
        content: The main text content of the message.
        embed_data: Optional dictionary to be sent as a formatted JSON embed.
    """
    if not settings.DISCORD_WEBHOOK_URL:
        return

    message = {"content": content}

    if embed_data:
        message["embeds"] = [
            {
                "description": f"```json\n{json.dumps(embed_data, indent=2, ensure_ascii=False)}\n```",
                "color": 5814783,  # A nice blue color
            }
        ]

    async with httpx.AsyncClient() as client:
        try:
            await client.post(settings.DISCORD_WEBHOOK_URL, json=message)
        except httpx.RequestError as e:
            # In a real app, you'd want to log this error.
            print(f"Error sending Discord webhook: {e}")
