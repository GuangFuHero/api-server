from pydantic import Field
from pydantic_settings import BaseSettings


class OpsConfig(BaseSettings):
    """
    This file is for DevOps for setting up related parameters.

    Field attribute brief intro

    Args:
        default: Any
        default_factory: Callable[[], Any] | None = _Unset, (accept callable function or lambda function)
        alias: str | None = _Unset
        alias_priority: int | None

    Notes:
        validator accepted parameters: (cls, value, values, config, field)

    """

    DEPLOY_ENV: str = Field(..., env="DEPLOY_ENV")
    APP_TITLE: str = Field(..., env="APP_TITLE")

    model_config = {"env_file": ".env", "extra": "ignore"}
