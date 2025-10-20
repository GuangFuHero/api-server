from fastapi import APIRouter, Depends, HTTPException, Query, Security, Request
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List, Literal
import asyncio

from .. import crud, models, schemas
from ..crud import (
    get_full_supply,
    supply_merge_item_counts,
    supply_batch_increment_received,
)
from ..database import get_db
from ..api_key import require_modify_api_key
from ..services.discord_webhook import (
    send_discord_message,
    format_supply_notification,
    format_supply_patch_notification,
)

router = APIRouter(
    prefix="/supplies",
    tags=["供應單（Supplies）"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=schemas.SupplyCollection, summary="取得供應單清單")
def list_supplies(
    request: Request,
    embed: Optional[str] = Query(None, enum=["all"]),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    取得供應單清單 (分頁)

    - order_by: 指定時間排序方式，可選 "asc" (由舊到新) 或 "desc" (由新到舊)，預設為 desc (最新的在前)
    """
    order_by = desc(models.Supply.updated_at)

    supplies = crud.get_multi(
        db, model=models.Supply, skip=offset, limit=limit, order_by=order_by
    )

    if embed == "all":
        supplies = (
            db.query(models.Supply)
            .options(joinedload(models.Supply.supplies))
            .filter(models.Supply.id.in_([s.id for s in supplies]))
            .all()
        )

    # 使用 crud.count 取得總數
    total = crud.count(db, model=models.Supply)
    next_link = crud.build_next_link(request, limit=limit, offset=offset, total=total)
    return {
        "member": supplies,
        "totalItems": total,
        "limit": limit,
        "offset": offset,
        "next": next_link,
    }


@router.post(
    "", response_model=schemas.SupplyWithPin, status_code=201, summary="建立供應單"
)
async def create_supply(
    supply_in: schemas.SupplyCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    建立供應單 (注意：同時建立 supply_items 的邏輯需在 crud 中客製化)
    """
    # This requires custom logic in crud.py to handle the nested `supplies` object
    created_supply = crud.create_supply_with_items(db, obj_in=supply_in)

    # 取得真實客戶端 IP（考慮反向代理）
    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.headers.get("x-real-ip", "")
        or (request.client.host if request.client else "unknown")
    )
    user_agent = request.headers.get("user-agent", "unknown")

    # 格式化通知訊息
    message_content = format_supply_notification(
        supply_data=supply_in.model_dump(mode="json"),
        supply_id=created_supply.id,
        created_at=created_supply.created_at,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    # Send Discord notification in background
    asyncio.create_task(send_discord_message(content=message_content))

    return created_supply


# 在 patch_supply 禁止更新已全部到貨的供應單
@router.patch(
    "/{id}",
    response_model=schemas.Supply,
    status_code=200,
    summary="更新供應單",
    # dependencies=[Security(require_modify_api_key)],
)
async def patch_supply(
    id: str,
    supply_in: schemas.SupplyPatch,
    request: Request,
    db: Session = Depends(get_db)
):
    db_supply = crud.get_by_id(db, models.Supply, id)
    if db_supply is None:
        raise HTTPException(status_code=404, detail="Supply not found")

    if crud.is_completed_supply(db_supply):
        raise HTTPException(
            status_code=400, detail="Completed supply orders cannot be edited."
        )

    # PIN 檢核
    # if db_supply.valid_pin and db_supply.valid_pin != supply_in.valid_pin:
    #     raise HTTPException(status_code=400, detail="The PIN you entered is incorrect.")

    # 更新供應單
    updated_supply = crud.update(db, db_obj=db_supply, obj_in=supply_in)

    # 取得真實客戶端 IP（考慮反向代理）
    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.headers.get("x-real-ip", "")
        or (request.client.host if request.client else "unknown")
    )
    user_agent = request.headers.get("user-agent", "unknown")

    # 取得更新的欄位
    updated_fields = supply_in.model_dump(exclude_unset=True)

    # 格式化並發送通知
    message_content = format_supply_patch_notification(
        supply_id=id,
        updated_fields=updated_fields,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    # Send notification to Discord in the background
    asyncio.create_task(send_discord_message(content=message_content))

    return updated_supply


@router.get("/{id}", response_model=schemas.Supply, summary="取得特定供應單")
def get_supply(id: str, db: Session = Depends(get_db)):
    """
    取得單一供應單 (包含其所有物資項目)
    """
    db_supply = (
        db.query(models.Supply)
        .options(joinedload(models.Supply.supplies))
        .filter(models.Supply.id == id)
        .first()
    )
    if db_supply is None:
        raise HTTPException(status_code=404, detail="Supply not found")
    return db_supply


@router.post("/{id}", response_model=schemas.Supply)
def update_supply(
    id: str,
    supply_item_in: List[schemas.SupplyItemUpdate],
    db: Session = Depends(get_db),
):
    """
    將 payload.data 中的各項目依據 id 對應到 supply_item，
    執行 received_count += count 的批次更新，並回傳更新後的 Supply。
    """
    merged = supply_merge_item_counts([item.model_dump() for item in supply_item_in])
    updated_supply = supply_batch_increment_received(db, id, merged)
    return updated_supply
