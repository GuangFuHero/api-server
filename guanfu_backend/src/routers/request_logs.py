from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(prefix="/request-logs", tags=["request-logs"])


@router.get("/", response_model=List[schemas.RequestLog])
def get_request_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    method: Optional[str] = Query(None),
    status_code: Optional[int] = Query(None),
    path: Optional[str] = Query(None),
    ip: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get request logs with optional filtering."""
    return crud.get_request_logs(
        db=db,
        skip=skip,
        limit=limit,
        method=method,
        status_code=status_code,
        path=path,
        ip=ip,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/count")
def get_request_logs_count(
    method: Optional[str] = Query(None),
    status_code: Optional[int] = Query(None),
    path: Optional[str] = Query(None),
    ip: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get count of request logs with optional filtering."""
    count = crud.count_request_logs(
        db=db,
        method=method,
        status_code=status_code,
        path=path,
        ip=ip,
        start_date=start_date,
        end_date=end_date
    )
    return {"count": count}


@router.get("/{log_id}", response_model=schemas.RequestLog)
def get_request_log(log_id: str, db: Session = Depends(get_db)):
    """Get a specific request log by ID."""
    request_log = crud.get_request_log_by_id(db=db, log_id=log_id)
    if not request_log:
        raise HTTPException(status_code=404, detail="Request log not found")
    return request_log


@router.get("/resource/{resource_id}", response_model=List[schemas.RequestLog])
def get_request_logs_by_resource(
    resource_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get request logs for a specific resource ID."""
    return crud.get_request_logs_by_resource_id(
        db=db,
        resource_id=resource_id,
        skip=skip,
        limit=limit
    )


@router.delete("/{log_id}")
def delete_request_log(log_id: str, db: Session = Depends(get_db)):
    """Delete a request log by ID."""
    success = crud.delete_request_log(db=db, log_id=log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request log not found")
    return {"message": "Request log deleted successfully"}
