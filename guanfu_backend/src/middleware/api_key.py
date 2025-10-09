from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from starlette import status
from starlette.requests import Request

from ..config import settings

API_KEY_HEADER = "x-api-key"
AUTHORIZATION_HEADER = "authorization"
BEARER_PREFIX = "bearer "


def _parse_allowlist(raw_values: str) -> set[str]:
    """Turn a comma-separated allowlist into a set of keys."""
    return {item.strip() for item in raw_values.split(",") if item.strip()}


def _allowed_keys() -> set[str]:
    return _parse_allowlist(settings.ALLOW_MODIFY_API_KEY_LIST)


api_key_header_scheme = APIKeyHeader(name="X-Api-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def extract_api_key(request: Request) -> str:
    """Return the provided API key from either X-Api-Key or Authorization headers."""
    key = request.headers.get(API_KEY_HEADER, "").strip()
    if key:
        return key
    authorization = request.headers.get(AUTHORIZATION_HEADER, "")
    if authorization.lower().startswith(BEARER_PREFIX):
        return authorization[len(BEARER_PREFIX) :].strip()
    return ""


async def require_modify_api_key(
    request: Request,
    _api_key_from_header: str | None = Security(api_key_header_scheme),
    _bearer_credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> str:
    allowed = _allowed_keys()
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Modification not allowed",
        )

    key = extract_api_key(request)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Modification not allowed",
        )

    if key not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return key


async def admin_authorization(
    request: Request,
    _api_key_from_header: str | None = Security(api_key_header_scheme),
    _bearer_credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    allowed = settings.ADMIN_API_KEY
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Modification not allowed",
        )

    key = extract_api_key(request)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Modification not allowed",
        )

    if key != allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return key
