"""
Discord Webhook 服務

提供 Discord 通知訊息的格式化和發送功能。
"""

import httpx
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Union

from ..config import settings
from .. import schemas, models

logger = logging.getLogger(__name__)


def _format_timestamp(created_at: Union[int, float, datetime]) -> str:
    """
    將時間戳或 datetime 物件轉換為 ISO 8601 格式字串

    Args:
        created_at: UNIX timestamp (int/float) 或 datetime 物件

    Returns:
        str: ISO 8601 格式的時間字串 (例如: "2024-12-04 15:45:30 UTC")
    """
    if isinstance(created_at, (int, float)):
        created_at = datetime.fromtimestamp(created_at, tz=timezone.utc)
    elif isinstance(created_at, datetime) and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return created_at.strftime('%Y-%m-%d %H:%M:%S UTC')


def _format_role_type_display(role_type: str, role_status: Optional[str] = None) -> str:
    """
    格式化角色類型顯示文字
    
    Args:
        role_type: 角色類型
        role_status: 角色狀態（可選）
    
    Returns:
        str: 格式化後的角色類型顯示文字
    """
    if role_status:
        return f"{role_type} / {role_status}"
    return role_type


def format_human_resource_notification(
    resource_data: schemas.HumanResourceCreate,
    resource_id: str,
    created_at: Union[int, float, datetime],
    client_ip: str,
    user_agent: str,
) -> str:
    """
    格式化人力需求通知訊息

    Args:
        resource_data: 人力需求資料 (HumanResourceCreate schema)
        resource_id: 資料庫 ID
        created_at: 建立時間 (datetime 物件或 UNIX timestamp)
        client_ip: 客戶端 IP
        user_agent: 使用者代理字串

    Returns:
        str: 格式化後的 Discord 訊息內容
    """
    # 格式化時間為 ISO 8601 格式（國際標準）
    time_str = _format_timestamp(created_at)

    # 構建訊息
    type_display = _format_role_type_display(resource_data.role_type, resource_data.role_status)

    unit = resource_data.headcount_unit or "人"

    notes_parts = []
    if resource_data.shift_notes:
        notes_parts.append(resource_data.shift_notes)
    if resource_data.assignment_notes:
        notes_parts.append(resource_data.assignment_notes)
    notes = "\n".join(notes_parts) if notes_parts else "無"

    message = f"""有人新增人力需求了(開單) 🛠️
標題: {resource_data.role_name}
需求類型: {type_display}
需求人數: {resource_data.headcount_need} {unit}
備註: {notes}
發出時間: {time_str}
資料庫ID: {resource_id}
IP: {client_ip}
User-Agent: {user_agent}"""

    return message


def format_supply_notification(
    supply_data: schemas.SupplyCreate,
    supply_id: str,
    created_at: Union[int, float, datetime],
    client_ip: str,
    user_agent: str,
) -> str:
    """
    格式化物資需求通知訊息

    Args:
        supply_data: 物資需求資料 (SupplyCreate schema)
        supply_id: 資料庫 ID
        created_at: 建立時間 (datetime 物件或 UNIX timestamp)
        client_ip: 客戶端 IP
        user_agent: 使用者代理字串

    Returns:
        str: 格式化後的 Discord 訊息內容
    """
    # 構建物資項目資訊
    supplies_dict = supply_data.supplies
    item_str = ""

    if isinstance(supplies_dict, dict):
        # 取得物資名稱和數量
        item_name = supplies_dict.get("name", "未知物資")
        total_number = supplies_dict.get("total_number", 0)
        item_str = f"{item_name} x{total_number}"

    name = supply_data.name or ""
    phone = supply_data.phone or ""
    address = supply_data.address or ""
    notes = supply_data.notes or ""

    message = f"""物資需求出現了 🐝
Name: {name}
ID: {supply_id}
Phone: {phone}
Address: {address}
Item: {item_str}
Notes: {notes}
IP: {client_ip}
User-Agent: {user_agent}"""

    return message


def format_human_resource_patch_notification(
    resource_id: str,
    resource: models.HumanResource,
    client_ip: str,
    user_agent: str,
) -> str:
    """
    格式化人力需求更新通知訊息

    Args:
        resource_id: 資料庫 ID
        resource: 完整的資源資料 (HumanResource model)
        client_ip: 客戶端 IP
        user_agent: 使用者代理字串

    Returns:
        str: 格式化後的 Discord 訊息內容
    """
    unit = resource.headcount_unit or "人"

    message = f"""有人報名人力需求了 (報名) 👷🏻
標題: {resource.role_name} ({resource_id})
報名/需求人數: {resource.headcount_got}/{resource.headcount_need} {unit}
IP: {client_ip}
User-Agent: {user_agent}"""

    return message


def format_supply_patch_notification(
    supply_id: str,
    updated_supply: "models.Supply",
    updated_fields: schemas.SupplyPatch,
    client_ip: str,
    user_agent: str,
) -> str:
    """
    格式化物資需求更新通知訊息

    Args:
        supply_id: 資料庫 ID
        updated_supply: 更新後的完整 Supply 物件
        updated_fields: 更新的欄位 (SupplyPatch schema)
        client_ip: 客戶端 IP
        user_agent: 使用者代理字串

    Returns:
        str: 格式化後的 Discord 訊息內容
    """
    # 構建更新欄位列表
    updates = []
    if updated_fields.name is not None:
        updates.append(f"  - name: {updated_fields.name}")
    if updated_fields.address is not None:
        updates.append(f"  - address: {updated_fields.address}")
    if updated_fields.phone is not None:
        updates.append(f"  - phone: {updated_fields.phone}")
    if updated_fields.notes is not None:
        updates.append(f"  - notes: {updated_fields.notes}")

    fields_str = "\n".join(updates) if updates else "  - (無更新)"
    
    # 構建物資項目資訊
    supply_items = []
    if hasattr(updated_supply, 'supplies') and updated_supply.supplies:
        for item in updated_supply.supplies:
            received = item.received_count if item.received_count is not None else 0
            total = item.total_number
            unit = item.unit if item.unit else ""
            name = item.name if item.name else "未知物資"
            supply_items.append(f"  - {name}: {received}/{total} {unit}")
    
    supply_items_str = "\n".join(supply_items) if supply_items else "  - (無物資項目)"

    message = f"""有人更新物資需求了 (物資提供) ✏️
資料庫ID: {supply_id}
聯絡人: {updated_supply.name or '未提供'}
更新欄位:
{fields_str}
物資項目狀態:
{supply_items_str}
IP: {client_ip}
User-Agent: {user_agent}"""

    return message


async def send_discord_message(content: str, embed_data: Optional[dict] = None):
    """
    發送訊息到 Discord webhook

    Args:
        content: 訊息主要內容
        embed_data: 可選的嵌入資料，將以 JSON 格式顯示

    Note:
        如果 DISCORD_WEBHOOK_URL 未設定，函數將直接返回不執行任何操作
    """
    if not settings.DISCORD_WEBHOOK_URL:
        logger.warning("Discord webhook URL not configured. Skipping webhook notification.")
        return

    message = {"content": content}

    if embed_data:
        message["embeds"] = [
            {
                "description": f"```json\n{json.dumps(embed_data, indent=2, ensure_ascii=False)}\n```",
                "color": 5814783,  # A nice blue color
            }
        ]

    logger.info("Sending Discord webhook: content length=%d, embed=%s", 
            len(content), "yes" if embed_data else "no")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(settings.DISCORD_WEBHOOK_URL, json=message)
            response.raise_for_status()  # Raise an exception for bad status codes
            logger.info("Discord webhook sent successfully. Status: %d", response.status_code)
        except httpx.RequestError as e:
            logger.error("Error sending Discord webhook: %s", e, exc_info=True)
        except httpx.HTTPStatusError as e:
            logger.error(
                "Error response from Discord webhook: %d - %s",
                e.response.status_code,
                e.response.text,
                exc_info=True,
            )
