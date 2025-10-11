from fastapi import APIRouter, Depends, HTTPException, Query, Security, Request
from sqlalchemy.orm import Session
from typing import Optional
from .. import crud, models, schemas
from ..database import get_db
from ..api_key import require_modify_api_key
from ..enum_serializer import PlaceTypeEnum, PlaceStatusEnum

router = APIRouter(
    prefix="/places",
    tags=["地點/場所（Places）"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=schemas.PlaceCollection, summary="取得地點/場所清單")
def list_places(
        request: Request,
        status: Optional[PlaceStatusEnum] = Query(None),
        type: Optional[PlaceTypeEnum] = Query(None),
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db)
):
    """
    取得地點/場所清單 (分頁)

    - **status**: 過濾狀態 (可選)
    - **type**: 過濾類型 (可選)
    - **limit**: 每頁筆數 (預設50, 最大500)
    - **offset**: 偏移量 (預設0)
    """
    filters = {"status": status, "type": type}
    places = crud.get_multi(db, models.Place, skip=offset, limit=limit, **filters)
    total = crud.count(db, models.Place, **filters)
    next_link = crud.build_next_link(request, limit=limit, offset=offset, total=total)
    return {
        "member": places,
        "totalItems": total,
        "limit": limit,
        "offset": offset,
        "next": next_link
    }


@router.post("", response_model=schemas.Place, status_code=201, summary="建立地點/場所")
def create_place(
        place_in: schemas.PlaceCreate, db: Session = Depends(get_db)
):
    """
    建立新的地點/場所

    必填欄位:
    - name: 名稱
    - address: 地址
    - coordinates: 座標 (JSONB: {lat: float, lng: float})
    - type: 類型
    - status: 狀態
    - contact_name: 聯絡人姓名
    - contact_phone: 聯絡電話
    """
    return crud.create(db, models.Place, obj_in=place_in)


@router.get("/{id}", response_model=schemas.Place, summary="取得特定地點/場所")
def get_place(id: str, db: Session = Depends(get_db)):
    """
    根據 ID 取得單一地點/場所
    """
    db_place = crud.get_by_id(db, models.Place, id)
    if db_place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return db_place


@router.patch(
    "/{id}",
    response_model=schemas.Place,
    summary="更新特定地點/場所",
    dependencies=[Security(require_modify_api_key)],
)
def patch_place(
        id: str, place_in: schemas.PlacePatch, db: Session = Depends(get_db)
):
    """
    更新地點/場所 (部分欄位)

    需要 API Key 認證 (透過 X-Api-Key header 或 Authorization: Bearer token)

    所有欄位皆為可選，僅更新提供的欄位。
    """
    db_place = crud.get_by_id(db, models.Place, id)
    if db_place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return crud.update(db, db_obj=db_place, obj_in=place_in)
