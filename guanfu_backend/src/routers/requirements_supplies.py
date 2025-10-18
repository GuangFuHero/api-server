from fastapi import APIRouter, Depends, HTTPException, Query, Security, Request
from sqlalchemy.orm import Session
from typing import Optional
from .. import crud, models, schemas
from ..database import get_db
from ..api_key import require_modify_api_key
from ..schemas import RequirementsSuppliesTypeEnum

router = APIRouter(
    prefix="/requirements_supplies",
    tags=["物資需求（Requirements Supplies）"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=schemas.RequirementsSuppliesCollection, summary="取得物資需求清單")
def list_requirements_supplies(
        request: Request,
        place_id: Optional[str] = Query(None, description="篩選特定場所的物資需求"),
        required_type: Optional[RequirementsSuppliesTypeEnum] = Query(None, description="篩選特定類型的物資需求"),
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db)
):
    """
    取得物資需求清單 (分頁)

    支援過濾條件：
    - place_id: 場所 ID
    - required_type: 需求類型
    """
    filters = {"place_id": place_id, "required_type": required_type}
    requirements = crud.get_multi(
        db,
        models.RequirementsSupplies,
        skip=offset,
        limit=limit,
        order_by=models.RequirementsSupplies.updated_at.desc(),
        **filters
    )
    total = crud.count(db, models.RequirementsSupplies, **filters)
    next_link = crud.build_next_link(request, limit=limit, offset=offset, total=total)
    return {"member": requirements, "totalItems": total, "limit": limit, "offset": offset, "next": next_link}


@router.post(
    "",
    response_model=schemas.RequirementsSupplies,
    status_code=201,
    summary="建立物資需求",
    dependencies=[Security(require_modify_api_key)],
)
def create_requirement_supply(
        requirement_in: schemas.RequirementsSuppliesCreate, db: Session = Depends(get_db)
):
    """
    建立新物資需求

    必填欄位：
    - place_id: 場所 ID
    - required_type: 需求類型
    - name: 需求名稱
    - unit: 單位
    - require_count: 需求數量

    選填欄位：
    - received_count: 已滿足數量（預設為 0）

    需要 API Key 權限
    """
    # Verify that the place_id exists
    place = crud.get_by_id(db, models.Place, requirement_in.place_id)
    if not place:
        raise HTTPException(status_code=404, detail=f"Place with id {requirement_in.place_id} not found")

    return crud.create(db, models.RequirementsSupplies, obj_in=requirement_in)


@router.get("/{id}", response_model=schemas.RequirementsSupplies, summary="取得特定物資需求")
def get_requirement_supply(id: str, db: Session = Depends(get_db)):
    """
    取得單一物資需求詳細資訊
    """
    db_requirement = crud.get_by_id(db, models.RequirementsSupplies, id)
    if db_requirement is None:
        raise HTTPException(status_code=404, detail="Requirement Supply not found")
    return db_requirement


@router.patch(
    "/{id}",
    response_model=schemas.RequirementsSupplies,
    summary="更新特定物資需求",
    dependencies=[Security(require_modify_api_key)],
)
def patch_requirement_supply(
        id: str, requirement_in: schemas.RequirementsSuppliesPatch, db: Session = Depends(get_db)
):
    """
    更新物資需求資訊 (部分欄位)

    需要 API Key 權限
    """
    db_requirement = crud.get_by_id(db, models.RequirementsSupplies, id)
    if db_requirement is None:
        raise HTTPException(status_code=404, detail="Requirement Supply not found")

    # If place_id is being updated, verify it exists
    if requirement_in.place_id is not None:
        place = crud.get_by_id(db, models.Place, requirement_in.place_id)
        if not place:
            raise HTTPException(status_code=404, detail=f"Place with id {requirement_in.place_id} not found")

    return crud.update(db, db_obj=db_requirement, obj_in=requirement_in)


@router.delete(
    "/{id}",
    status_code=204,
    summary="刪除特定物資需求",
    dependencies=[Security(require_modify_api_key)],
)
def delete_requirement_supply(id: str, db: Session = Depends(get_db)):
    """
    刪除物資需求

    需要 API Key 權限
    """
    db_requirement = crud.get_by_id(db, models.RequirementsSupplies, id)
    if db_requirement is None:
        raise HTTPException(status_code=404, detail="Requirement Supply not found")

    db.delete(db_requirement)
    db.commit()
    return None
