from fastapi import APIRouter, Depends, HTTPException, Query, Security, Request
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List, Literal
from .. import crud, models, schemas
from ..crud import (
    get_full_supply,
    supply_merge_item_counts,
    supply_batch_increment_received,
)
from ..database import get_db
from ..api_key import require_modify_api_key

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
    order_by: Optional[Literal["asc", "desc"]] = Query(
        "desc", description="時間排序方式：asc 或 desc，預設為 desc"
    ),
    db: Session = Depends(get_db),
):
    """
    取得供應單清單 (分頁)

    - order_by: 指定時間排序方式，可選 "asc" (由舊到新) 或 "desc" (由新到舊)，預設為 desc (最新的在前)
    """
    if order_by == "asc":
        order_clause = models.Supply.updated_at.asc()
    else:
        # 預設使用 desc，確保有明確的排序
        order_clause = models.Supply.updated_at.desc()

    supplies = crud.get_multi(
        db, model=models.Supply, skip=offset, limit=limit, order_by=order_clause
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
def create_supply(supply_in: schemas.SupplyCreate, db: Session = Depends(get_db)):
    """
    建立供應單 (注意：同時建立 supply_items 的邏輯需在 crud 中客製化)
    """
    # This requires custom logic in crud.py to handle the nested `supplies` object
    return crud.create_supply_with_items(db, obj_in=supply_in)


# 在 patch_supply 禁止更新已全部到貨的供應單
@router.patch(
    "/{id}",
    response_model=schemas.Supply,
    status_code=200,
    summary="更新供應單",
    # dependencies=[Security(require_modify_api_key)],
)
def patch_supply(id: str, supply_in: schemas.SupplyPatch, db: Session = Depends(get_db)):
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

    return crud.update(db, db_obj=db_supply, obj_in=supply_in)


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
