from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, Form, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import LineTokenResponse, LineUserInfoResponse
from ..services.line_auth import (
    build_authorize_url,
    exchange_token_authorization_code,
    exchange_token_refresh,
    revoke_token,
    userinfo_from_id_token,
)

router = APIRouter(prefix="/line", tags=["OAuth2 (LINE)"], include_in_schema=False)


@router.get("/authorize", summary="取得LINE 授權入口")
def authorize(
        redirect_uri: str = Query(..., description="LINE OAuth 回呼 URL"),
        prompt: Optional[str] = Query(default=None),
        response_mode: Optional[str] = Query(default=None),
        disable_auto_login: Optional[bool] = Query(default=None),
        db: Session = Depends(get_db),
):
    url = build_authorize_url(
        db,
        redirect_uri=redirect_uri,
        prompt=prompt,
        response_mode=response_mode,
        disable_auto_login=disable_auto_login
    )
    return RedirectResponse(url)


@router.get("/token", summary="依照line授權碼(code)交換token", response_model=LineTokenResponse)
async def token_exchange(request: Request, db: Session = Depends(get_db)):
    q = dict(request.query_params)
    if "error" in q:
        return JSONResponse(status_code=400, content={"error": q.get("error"), "error_description": q.get("error_description")})
    code = q.get("code")
    state = q.get("state")
    if not code or not state:
        raise HTTPException(status_code=400, detail="缺少 code 或 state")
    token_payload = await exchange_token_authorization_code(db, code, state)
    return token_payload


@router.post("/refresh_token", response_model=LineTokenResponse, summary="依照refresh_token交換token")
async def token(
        grant_type: str = Form(..., pattern="^(authorization_code|refresh_token)$"),
        code: Optional[str] = Form(default=None),
        refresh_token: Optional[str] = Form(default=None),
        db: Session = Depends(get_db),
):
    if grant_type == "authorization_code":
        if not code:
            raise HTTPException(status_code=400, detail="缺少 code")
        # 這裡無 state（DOT 習慣是在 authorize/callback 完成），若你要合併流程可改為在 body 帶 state
        raise HTTPException(status_code=400, detail="authorization_code 請使用 /line/token 完成交換")
    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(status_code=400, detail="缺少 refresh_token")
        return await exchange_token_refresh(db, refresh_token)


@router.post("/revoke", summary="撤銷token")
async def revoke(access_token: str = Form(...)):
    ok = await revoke_token(access_token)
    return {"revoked": ok}
