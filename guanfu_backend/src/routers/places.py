from fastapi import APIRouter, Depends, HTTPException, Query, Security, Request
from sqlalchemy.orm import Session
from typing import Optional
from .. import crud, models, schemas
from ..database import get_db
from ..api_key import require_modify_api_key
from ..schemas import PlaceStatusEnum, PlaceTypeEnum

router = APIRouter(
    prefix="/places",
    tags=["場所（Places）"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=schemas.PlaceCollection, summary="取得場所清單")
def list_places(
        request: Request,
        status: Optional[PlaceStatusEnum] = Query(None),
        type: Optional[PlaceTypeEnum] = Query(None),
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db)
):
    """
    取得場所清單 (分頁)

    支援過濾條件：
    - status: 場所狀態 (開放/暫停/關閉)
    - type: 場所類型 (醫療/加水/廁所/洗澡/避難/住宿/物資/心理援助)
    """
    filters = {"status": status, "type": type}
    places = crud.get_multi(db, models.Place, skip=offset, limit=limit, order_by=models.Place.updated_at.desc(), **filters)
    total = crud.count(db, models.Place, **filters)
    next_link = crud.build_next_link(request, limit=limit, offset=offset, total=total)
    return {"member": places, "totalItems": total, "limit": limit, "offset": offset, "next": next_link}


@router.post(
    "",
    response_model=schemas.Place,
    status_code=201,
    summary="建立場所",
    dependencies=[Security(require_modify_api_key)],
)
def create_place(
        place_in: schemas.PlaceCreate, db: Session = Depends(get_db)
):
    """
    建立新場所

    必填欄位：
    - name: 場所名稱
    - address: 地址
    - coordinates: 座標 (JSONB 格式)
    - type: 類型
    - status: 狀態
    - contact_name: 聯絡人姓名
    - contact_phone: 聯絡電話

    需要 API Key 權限
    """
    return crud.create(db, models.Place, obj_in=place_in)


@router.get("/{id}", response_model=schemas.Place, summary="取得特定場所")
def get_place(id: str, db: Session = Depends(get_db)):
    """
    取得單一場所詳細資訊
    """
    db_place = crud.get_by_id(db, models.Place, id)
    if db_place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return db_place


@router.patch(
    "/{id}",
    response_model=schemas.Place,
    summary="更新特定場所",
    dependencies=[Security(require_modify_api_key)],
)
def patch_place(
        id: str, place_in: schemas.PlacePatch, db: Session = Depends(get_db)
):
    """
    更新場所資訊 (部分欄位)

    需要 API Key 權限
    """
    db_place = crud.get_by_id(db, models.Place, id)
    if db_place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return crud.update(db, db_obj=db_place, obj_in=place_in)
