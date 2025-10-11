from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Security, Request
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..services.line_auth import verify_user_token

router = APIRouter(
    prefix="/supply_providers",
    tags=["供應提供者（Supply Providers）"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=schemas.SupplyProviderCollection, summary="取得物資供應提供者清單")
def list_supply_providers(
        request: Request,
        supply_item_id: Optional[str] = Query(None),
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db)
):
    """
    取得物資供應提供者清單 (分頁)
    """
    filters = {"supply_item_id": supply_item_id}
    providers = crud.get_multi(
        db,
        models.SupplyProvider,
        skip=offset,
        limit=limit,
        order_by=models.SupplyProvider.updated_at.desc(),
        **filters,
    )
    total = crud.count(db, models.SupplyProvider, **filters)
    next_link = crud.build_next_link(request, limit=limit, offset=offset, total=total)
    return {"member": providers, "totalItems": total, "limit": limit, "offset": offset, "next": next_link}


@router.post(
    "",
    response_model=schemas.SupplyProvider,
    status_code=201,
    summary="建立物資供應提供者",
    dependencies=[Depends(verify_user_token)],  # 需要 Token 驗證
)
def create_supply_provider(
    provider_in: schemas.SupplyProviderCreate,
    db: Session = Depends(get_db),
):
    """
    建立物資供應提供者
    """
    # 和 go 同邏輯
    if not crud.get_by_id(db, models.SupplyItem, provider_in.supply_item_id):
        raise HTTPException(status_code=404, detail="Supply Item not found")

    return crud.create(db, models.SupplyProvider, obj_in=provider_in)


@router.patch(
    "/{id}",
    response_model=schemas.SupplyProvider,
    status_code=200,
    summary="更新特定物資供應提供者",
    dependencies=[Depends(verify_user_token)],  # 需要 Token 驗證
)
def patch_supply_provider(
    id: str,
    provider_in: schemas.SupplyProviderPatch,
    db: Session = Depends(get_db),
):
    """
    更新物資供應提供者 (部分欄位)
    """
    update_data = provider_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided")

    db_provider = crud.get_by_id(db, models.SupplyProvider, id)
    if db_provider is None:
        raise HTTPException(status_code=404, detail="Supply Provider not found")

    new_supply_item_id = update_data.get("supply_item_id")
    if new_supply_item_id is not None:
        if not crud.get_by_id(db, models.SupplyItem, new_supply_item_id):
            raise HTTPException(status_code=404, detail="Supply Item not found")

    return crud.update(db, db_obj=db_provider, obj_in=provider_in)


@router.get("/{id}", response_model=schemas.SupplyProvider, summary="取得特定物資供應提供者")
def get_supply_provider(id: str, db: Session = Depends(get_db)):
    """
    取得單一物資供應提供者
    """
    db_provider = crud.get_by_id(db, models.SupplyProvider, id)
    if db_provider is None:
        raise HTTPException(status_code=404, detail="Supply Provider not found")
    return db_provider
