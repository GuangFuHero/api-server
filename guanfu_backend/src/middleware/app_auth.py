from logging import Logger

from fastapi import Header, HTTPException
from starlette import status

from ..config import settings

logger = Logger(__name__)


async def _validate_api_key(expected_key: str, provided_key: str | None):
    if not provided_key:
        logger.warn(f"Missing API key in request headers")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    if provided_key != expected_key:
        logger.warn(f"Invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


async def admin_authorization(x_api_key: str = Header(None)):
    await _validate_api_key(settings.ADMIN_API_KEY, x_api_key)
