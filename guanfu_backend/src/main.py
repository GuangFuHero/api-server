import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from psycopg2 import errors
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT
from sqlalchemy.orm import Session

from . import database
from .config import settings
from . import pubsub_service, background_processor
from .routers import (
    accommodations,
    human_resources,
    medical_stations,
    mental_health_resources,
    reports,
    request_logs,
    restrooms,
    shelters,
    shower_stations,
    supplies,
    supply_items,
    volunteer_organizations,
    water_refill_stations,
)


# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    # Create database tables to prevent "relation does not exist" errors
    database.init_db()
    
    # Start background processor for request logs
    await background_processor.log_processor.start()
    
    yield
    
    # Shutdown:
    # Stop background processor
    await background_processor.log_processor.stop()


# --- 根據環境動態設定 Swagger UI 的伺服器 URL ---
servers = [
    {"url": f"http://localhost:{settings.SERVER_PORT}", "description": "本地開發 (Dev)"},
    {"url": f"{settings.LAN_SERVER_URL}:{settings.SERVER_PORT}", "description": "LAN 主機環境 (Test On LAN)"},
]
if settings.ENVIRONMENT == "prod":
    servers.insert(
        0, {"url": settings.PROD_SERVER_URL, "description": "線上服務 (Production)"}
    )

# --- 建立 FastAPI 應用實例 ---
app = FastAPI(
    title=settings.APP_TITLE,
    version="v1.1.0",
    description="光復主站api",
    servers=servers,
    lifespan=lifespan,  # 使用 lifespan
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # 隱藏model schema
        "docExpansion": "none",  # 預設label收起
    },
)


# ===================================================================
# 全域異常處理器 (Global Exception Handlers)
# ===================================================================


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    自定義 Pydantic 驗證錯誤的處理器，
    將其格式化為更易讀的 {field: [error_message]} 格式，類似 Django REST Framework。
    """
    simplified_errors = {}
    for error in exc.errors():
        # error['loc'] 是一個元組，例如 ('body', 'status')，我們通常取最後一個作為欄位名
        field_name = str(error["loc"][-1]) if error["loc"] else "general"
        error_message = error["msg"]

        # 將錯誤訊息整理成列表
        if field_name not in simplified_errors:
            simplified_errors[field_name] = []
        simplified_errors[field_name].append(error_message)

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        content=simplified_errors,
    )


@app.exception_handler(IntegrityError)
async def integrity_error_exception_handler(request: Request, exc: IntegrityError):
    """
    攔截所有 SQLAlchemy 的 IntegrityError，並根據具體的錯誤類型回傳友善的錯誤訊息。
    """
    original_error = exc.orig

    # 判斷原始錯誤的具體類型
    if isinstance(original_error, errors.CheckViolation):
        constraint_name = original_error.diag.constraint_name
        detail = f"Input data violates check constraint '{constraint_name}'. Please provide a valid value."
        return JSONResponse(status_code=400, content={"detail": detail})

    if isinstance(original_error, errors.UniqueViolation):
        constraint_name = original_error.diag.constraint_name
        detail = f"A record with this value already exists (violates unique constraint '{constraint_name}')."
        return JSONResponse(status_code=409, content={"detail": detail})

    if isinstance(original_error, errors.NotNullViolation):
        column_name = original_error.diag.column_name
        detail = f"Required field '{column_name}' cannot be null."
        return JSONResponse(status_code=400, content={"detail": detail})

    if isinstance(original_error, errors.ForeignKeyViolation):
        constraint_name = original_error.diag.constraint_name
        detail = f"Foreign key constraint '{constraint_name}' failed. The referenced record may not exist."
        return JSONResponse(status_code=400, content={"detail": detail})

    logging.error(f"Unhandled IntegrityError: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected database integrity error occurred."},
    )


# --- 包含所有資源的 routers ---
app.include_router(shelters.router)
app.include_router(reports.router)
app.include_router(volunteer_organizations.router)
app.include_router(accommodations.router)
app.include_router(human_resources.router)
app.include_router(medical_stations.router)
app.include_router(mental_health_resources.router)
app.include_router(restrooms.router)
app.include_router(shower_stations.router)
app.include_router(water_refill_stations.router)
app.include_router(supplies.router)
app.include_router(supply_items.router)
app.include_router(request_logs.router)


# --- Request Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests to the database."""
    start_time = time.time()
    
    # Extract request information
    method = request.method
    path = request.url.path
    query = str(request.url.query) if request.url.query else None
    ip = request.client.host if request.client else None
    
    # Get headers (excluding sensitive ones)
    headers = {}
    for key, value in request.headers.items():
        if key.lower() not in ['authorization', 'cookie', 'x-api-key']:
            headers[key] = value
    
    # Get request body for non-GET requests (filter sensitive data)
    request_body = None
    if method != "GET":
        try:
            body = await request.body()
            if body:
                import json
                body_data = json.loads(body.decode('utf-8'))
                # Filter sensitive fields
                if isinstance(body_data, dict):
                    sensitive_fields = ['password', 'token', 'secret', 'key', 'authorization']
                    request_body = {k: v for k, v in body_data.items() 
                                  if not any(sensitive in k.lower() for sensitive in sensitive_fields)}
                else:
                    request_body = body_data
        except Exception:
            request_body = None
    
    # Process the request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Extract response information
    status_code = response.status_code
    
    # Get response body for logging
    result_data = None
    if hasattr(response, 'body'):
        try:
            import json
            if response.body:
                result_data = json.loads(response.body.decode('utf-8'))
        except Exception:
            result_data = None
    
    # Send to pubsub for asynchronous processing
    try:
        # Extract resource_id from path if it's a resource endpoint
        resource_id = None
        path_parts = path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] in [
            'shelters', 'accommodations', 'human-resources', 'medical-stations',
            'mental-health-resources', 'restrooms', 'shower-stations',
            'water-refill-stations', 'supplies', 'supply-items', 'reports',
            'volunteer-organizations'
        ]:
            resource_id = path_parts[1] if len(path_parts) > 1 else None
        
        # 限制記錄的資料大小以避免 pubsub 過載
        def limit_data_size(data, max_size=10000):
            if data and len(str(data)) > max_size:
                return {"truncated": True, "size": len(str(data))}
            return data
        
        # 準備要發送到 pubsub 的資料
        log_data = {
            'method': method,
            'path': path,
            'query': query,
            'ip': ip,
            'headers': limit_data_size(headers),
            'status_code': status_code,
            'error': None,  # Will be set if there's an exception
            'duration_ms': duration_ms,
            'request_body': limit_data_size(request_body),
            'result_data': limit_data_size(result_data),
            'resource_id': resource_id
        }
        
        # 發送到 pubsub (非阻塞)
        await pubsub_service.publish_request_log(log_data)
        
    except Exception as e:
        logging.error(f"Failed to publish request log to pubsub: {e}")
    
    return response
