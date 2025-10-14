from fastapi import APIRouter, Depends, HTTPException, Query, Security, Request
from sqlalchemy.orm import Session
from typing import Optional, Literal
from .. import crud, models, schemas
from ..database import get_db
from ..enum_serializer import HumanResourceRoleStatusEnum, HumanResourceRoleTypeEnum, HumanResourceStatusEnum
from ..pin_related import generate_pin
from ..api_key import require_modify_api_key

router = APIRouter(
    prefix="/human_resources",
    tags=["人力需求（Human Resources）"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=schemas.HumanResourceCollection, summary="取得人力需求清單")
def list_human_resources(
        request: Request,
        status: Optional[HumanResourceStatusEnum] = Query(None),
        role_status: Optional[HumanResourceRoleStatusEnum] = Query(None),
        role_type: Optional[HumanResourceRoleTypeEnum] = Query(None),
        limit: int = Query(20, ge=1, le=200),
        offset: int = Query(0, ge=0),
        order_by_time: Optional[Literal["asc", "desc"]] = Query(None, description="時間排序方式：asc 或 desc"),
        db: Session = Depends(get_db)
):
    """
    取得人力需求清單 (分頁)
    
    - order_by: 指定時間排序方式，可選 "asc" (由舊到新) 或 "desc" (由新到舊)
    """
    filters = {
        "status": status,
        "role_status": role_status,
        "role_type": role_type,
    }
    
    order_by = None
    if order_by_time == "asc":
        order_by = models.HumanResource.created_at.asc()
    elif order_by_time == "desc":
        order_by = models.HumanResource.created_at.desc()
    
    resources = crud.get_multi(
        db, 
        models.HumanResource, 
        skip=offset, 
        limit=limit,
        order_by=order_by,
        **filters
    )
    resources = crud.mask_id_if_field_equals(resources, "status", "completed")
    total = crud.count(db, models.HumanResource, **filters)
    next_link = crud.build_next_link(request, limit=limit, offset=offset, total=total)
    return {"member": resources, "totalItems": total, "limit": limit, "offset": offset, "next": next_link}


@router.post("", response_model=schemas.HumanResourceWithPin, status_code=201, summary="建立人力需求")
def create_human_resource(
        resource_in: schemas.HumanResourceCreate, db: Session = Depends(get_db)
):
    """
    建立人力需求/角色
    """
    if resource_in.headcount_got > resource_in.headcount_need:
        raise HTTPException(status_code=400, detail="headcount_got must be less than or equal to headcount_need.")
    return crud.create_with_input(db, models.HumanResource, obj_in=resource_in, valid_pin=generate_pin())


@router.get("/{id}", response_model=schemas.HumanResource, summary="取得特定人力需求")
def get_human_resource(id: str, db: Session = Depends(get_db)):
    """
    取得單一人力需求/角色
    """
    db_resource = crud.get_by_id(db, models.HumanResource, id)
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Human Resource not found")
    return db_resource


@router.patch(
    "/{id}",
    response_model=schemas.HumanResource,
    summary="更新特定人力需求",
    # dependencies=[Security(require_modify_api_key)],
)
def patch_human_resource(
        id: str, resource_in: schemas.HumanResourcePatch, db: Session = Depends(get_db)
):
    """
    更新人力需求/角色 (部分欄位)
    """
    db_resource = crud.get_by_id(db, models.HumanResource, id)
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Human Resource not found")
    # if db_resource.valid_pin and db_resource.valid_pin != resource_in.valid_pin:
    #     raise HTTPException(status_code=400, detail="The PIN you entered is incorrect.")
    if db_resource.status == HumanResourceRoleStatusEnum.completed.value:
        raise HTTPException(status_code=400, detail="Completed data cannot be edited.")

    # 人數供給>需求防呆
    if resource_in.headcount_need is not None or resource_in.headcount_got is not None:
        if resource_in.headcount_need == resource_in.headcount_got and resource_in.status == HumanResourceRoleStatusEnum.completed.value:
            raise HTTPException(status_code=400, detail="headcount_need and headcount_got are locked because their values are equal; updates are not allowed.")
        headcount_need = resource_in.headcount_need if resource_in.headcount_need is not None else db_resource.headcount_need
        headcount_got = resource_in.headcount_got if resource_in.headcount_got is not None else db_resource.headcount_got
        if headcount_got > headcount_need:
            raise HTTPException(status_code=400, detail="headcount_got must be less than or equal to headcount_need.")
    return crud.update(db, db_obj=db_resource, obj_in=resource_in)
