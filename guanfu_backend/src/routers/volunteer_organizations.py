from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..middleware.api_key import require_modify_api_key

router = APIRouter(
    prefix="/volunteer_organizations",
    tags=["志工招募單位（Volunteer Organizations）"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "", response_model=schemas.VolunteerOrgCollection, summary="取得志工招募單位清單"
)
def list_volunteer_orgs(
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    取得志工招募單位清單 (分頁)
    """
    orgs = crud.get_multi(db, models.VolunteerOrganization, skip=offset, limit=limit)
    total = crud.count(db, models.VolunteerOrganization)
    return {"member": orgs, "totalItems": total, "limit": limit, "offset": offset}


@router.post(
    "",
    response_model=schemas.VolunteerOrganization,
    status_code=201,
    summary="建立志工招募單位",
)
def create_volunteer_org(
    org_in: schemas.VolunteerOrgCreate, db: Session = Depends(get_db)
):
    """
    建立志工招募單位
    """
    return crud.create(db, models.VolunteerOrganization, obj_in=org_in)


@router.get(
    "/{id}",
    response_model=schemas.VolunteerOrganization,
    summary="取得特定志工招募單位",
)
def get_volunteer_org(id: str, db: Session = Depends(get_db)):
    """
    取得單一志工招募單位
    """
    db_org = crud.get_by_id(db, models.VolunteerOrganization, id)
    if db_org is None:
        raise HTTPException(status_code=404, detail="Volunteer Organization not found")
    return db_org


@router.patch(
    "/{id}",
    response_model=schemas.VolunteerOrganization,
    summary="更新特定志工招募單位",
    dependencies=[Security(require_modify_api_key)],
)
def patch_volunteer_org(
    id: str, org_in: schemas.VolunteerOrgPatch, db: Session = Depends(get_db)
):
    """
    更新志工招募單位 (部分欄位)
    """
    db_org = crud.get_by_id(db, models.VolunteerOrganization, id)
    if db_org is None:
        raise HTTPException(status_code=404, detail="Volunteer Organization not found")
    return crud.update(db, db_obj=db_org, obj_in=org_in)
