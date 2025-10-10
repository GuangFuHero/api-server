import base64
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

import httpx
from urllib.parse import urlencode
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..models import LineUser, LineSessionState

# LINE OAuth2 / OIDC endpoints
AUTH_URL = "https://access.line.me/oauth2/v2.1/authorize"
TOKEN_URL = "https://api.line.me/oauth2/v2.1/token"
USERINFO_URL = "https://api.line.me/oauth2/v2.1/userinfo"
VERIFY_URL = "https://api.line.me/oauth2/v2.1/verify"
REVOKE_URL = "https://api.line.me/oauth2/v2.1/revoke"

# Logger
logger = logging.getLogger(__name__)


# ====== Utility functions ======

def _generate_state() -> str:
    return secrets.token_urlsafe(32)


def _generate_nonce() -> str:
    return secrets.token_urlsafe(32)


def _generate_code_verifier() -> str:
    return secrets.token_urlsafe(64)


def _code_challenge_s256(code_verifier: str) -> str:
    h = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(h).decode("utf-8").rstrip("=")


# ====== Build Authorization URL ======

def build_authorize_url(
        db: Session,
        prompt: Optional[str] = None,
        response_mode: Optional[str] = None,
        disable_auto_login: Optional[bool] = None,
) -> str:
    """
    產生 LINE Login 授權頁 URL（PKCE + OIDC）
    """
    state = _generate_state()
    nonce = _generate_nonce()
    code_verifier = _generate_code_verifier()
    code_challenge = _code_challenge_s256(code_verifier)

    sess = LineSessionState(
        state=state,
        nonce=nonce,
        code_verifier=code_verifier,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(sess)
    db.commit()

    params = {
        "response_type": "code",
        "client_id": settings.LINE_CLIENT_ID,
        "redirect_uri": settings.LINE_REDIRECT_URI,
        "state": state,
        "scope": settings.LINE_SCOPES,  # e.g. "openid profile email"
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "ui_locales": "zh-TW",
    }
    if prompt:
        params["prompt"] = prompt
    if response_mode:
        params["response_mode"] = response_mode
    if disable_auto_login:
        params["disable_auto_login"] = "true"

    return f"{AUTH_URL}?{urlencode(params)}"


# ====== Exchange Token ======

async def exchange_token_authorization_code(db: Session, code: str, state: str) -> Dict:
    """
    授權碼換取 access_token / id_token，並驗證 ID Token + 更新使用者資料
    """
    sess: Optional[LineSessionState] = db.query(LineSessionState).filter(LineSessionState.state == state).first()
    if not sess or sess.consumed:
        raise HTTPException(status_code=400, detail="state 無效或已使用")
    if sess.expires_at and sess.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="state 已過期")

    async with httpx.AsyncClient(timeout=15) as client:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.LINE_REDIRECT_URI,
            "client_id": settings.LINE_CLIENT_ID,
            "client_secret": settings.LINE_CLIENT_SECRET,
            "code_verifier": sess.code_verifier,
        }
        token_resp = await client.post(TOKEN_URL, data=data)
        if token_resp.status_code != 200:
            logger.error(f"交換 token 失敗: {token_resp.text}")
            raise HTTPException(status_code=token_resp.status_code, detail="交換 token 失敗")

        token_json = token_resp.json()
        access_token = token_json.get("access_token")
        refresh_token = token_json.get("refresh_token")
        id_token = token_json.get("id_token")
        expires_in = token_json.get("expires_in", 0)

    if not access_token or not id_token:
        raise HTTPException(status_code=400, detail="缺少 access_token 或 id_token")

    # ====== 使用 LINE verify endpoint 驗證 ID Token ======
    async with httpx.AsyncClient(timeout=10) as client:
        verify_data = {
            "id_token": id_token,
            "client_id": settings.LINE_CLIENT_ID,
        }
        verify_resp = await client.post(VERIFY_URL, data=verify_data)
        if verify_resp.status_code != 200:
            logger.error(f"ID Token 驗證失敗: {verify_resp.text}")
            raise HTTPException(status_code=400, detail="ID Token 驗證失敗")
        
        decoded = verify_resp.json()
        logger.info(f"ID Token 驗證成功: {decoded}")

    # 驗證 nonce
    if decoded.get("nonce") != sess.nonce:
        raise HTTPException(status_code=400, detail="nonce 驗證失敗")

    line_user_id = decoded.get("sub")
    email = decoded.get("email")
    display_name = decoded.get("name")
    picture_url = decoded.get("picture")

    # ====== 從 userinfo 端點取更多資料 ======
    async with httpx.AsyncClient(timeout=10) as client:
        prof_resp = await client.get(USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
        if prof_resp.status_code == 200:
            prof = prof_resp.json()
            display_name = prof.get("name", display_name)
            picture_url = prof.get("picture", picture_url)
        else:
            logger.warning(f"userinfo 取得失敗: {prof_resp.text}")

    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=int(expires_in)) if expires_in else None

    user = db.query(LineUser).filter(LineUser.line_user_id == line_user_id).first()
    if not user:
        user = LineUser(
            line_user_id=line_user_id,
            display_name=display_name,
            picture_url=picture_url,
            email=email,
            email_granted=bool(email),
            scopes=settings.LINE_SCOPES,
            last_login_at=now,
            access_token=access_token,
            refresh_token=refresh_token,
            id_token=id_token,
            token_expires_at=expires_at,
            channel_id=str(settings.LINE_CLIENT_ID),
        )
        db.add(user)
    else:
        user.display_name = display_name
        user.picture_url = picture_url
        user.email = email
        user.email_granted = bool(email)
        user.last_login_at = now
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.id_token = id_token
        user.token_expires_at = expires_at

    sess.consumed = True
    db.commit()
    db.refresh(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "id_token": id_token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "line_user_id": user.line_user_id,
    }


# ====== Refresh Token ======

async def exchange_token_refresh(db: Session, refresh_token: str) -> Dict:
    """
    依 LINE 規範，用 refresh_token 交換新 access_token。
    """
    async with httpx.AsyncClient(timeout=15) as client:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.LINE_CLIENT_ID,
            "client_secret": settings.LINE_CLIENT_SECRET,
        }
        resp = await client.post(TOKEN_URL, data=data)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="刷新 token 失敗")

        token_json = resp.json()

    access_token = token_json.get("access_token")
    new_refresh_token = token_json.get("refresh_token", refresh_token)
    expires_in = token_json.get("expires_in", 0)

    # 同步更新使用者 token
    user = db.query(LineUser).filter(LineUser.refresh_token == refresh_token).first()
    if not user:
        raise HTTPException(status_code=404, detail="找不到對應的使用者")
    
    user.access_token = access_token
    user.refresh_token = new_refresh_token
    user.token_expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "id_token": user.id_token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "line_user_id": user.line_user_id,
    }


# ====== Revoke Token ======

async def revoke_token(access_token: str) -> bool:
    """
    撤銷 access_token。
    """
    async with httpx.AsyncClient(timeout=15) as client:
        data = {
            "access_token": access_token,
            "client_id": settings.LINE_CLIENT_ID,
            "client_secret": settings.LINE_CLIENT_SECRET,
        }
        resp = await client.post(REVOKE_URL, data=data)
        if resp.status_code == 200:
            return True
        raise HTTPException(status_code=resp.status_code, detail="撤銷失敗")


# ====== Userinfo (Local lookup) ======

def userinfo_from_id_token(db: Session, id_token: str) -> Dict:
    """
    根據本地已驗證的 id_token 找使用者資料。
    """
    user = db.query(LineUser).filter(LineUser.id_token == id_token).first()
    if not user:
        raise HTTPException(status_code=404, detail="找不到對應使用者")
    return {
        "sub": user.line_user_id,
        "name": user.display_name,
        "picture": user.picture_url,
        "email": user.email,
        "email_granted": user.email_granted,
        "scope": user.scopes,
    }
