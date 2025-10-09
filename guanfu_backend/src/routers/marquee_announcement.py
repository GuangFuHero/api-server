from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..middleware.app_auth import admin_authorization
from ..schemas import (
    MarqueeAnnouncement,
    MarqueeAnnouncementCollection,
    MarqueeAnnouncementCreate,
    MarqueeAnnouncementPatch,
)

router = APIRouter(
    prefix="/marquee_announcements",
    tags=["跑馬燈（Marquee Announcements）"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=MarqueeAnnouncementCollection, summary="取得跑馬燈清單")
def list_marquee_announcements(
    active: Optional[bool] = Query(True),
    limit: int = Query(3, ge=1, le=10),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    取得跑馬燈清單 (分頁)
    """
    filters = {"active": active}
    announcements = crud.get_multi(
        db,
        models.MarqueeAnnouncements,
        skip=offset,
        limit=limit,
        order_by=desc(models.MarqueeAnnouncements.updated_at),
        **filters
    )
    total = crud.count(db, models.MarqueeAnnouncements, **filters)
    return {
        "member": announcements,
        "totalItems": total,
        "limit": limit,
        "offset": offset,
    }


@router.post(
    "",
    response_model=MarqueeAnnouncement,
    summary="新增跑馬燈",
    dependencies=[Depends(admin_authorization)],
)
def create_marquee_announcement(
    announcement: MarqueeAnnouncementCreate, db: Session = Depends(get_db)
):
    return crud.create(db, models.MarqueeAnnouncements, announcement)


@router.patch(
    "/{id}",
    response_model=MarqueeAnnouncement,
    summary="更新跑馬燈",
    dependencies=[Depends(admin_authorization)],
)
def update_marquee_announcement(
    id: str, announcement: MarqueeAnnouncementPatch, db: Session = Depends(get_db)
):
    """
    更新跑馬燈 (部分欄位)
    """
    db_announcement = crud.get_by_id(db, models.MarqueeAnnouncements, id)
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Marquee announcement not found")
    return crud.update(db, db_obj=db_announcement, obj_in=announcement)
