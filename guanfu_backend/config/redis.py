from pydantic import Field, RedisDsn, field_validator
from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):
    """Field attribute brief intro

    Args:
        default: Any
        default_factory: Callable[[], Any] | None = _Unset, (accept callable function or lambda function)
        alias: str | None = _Unset
        alias_priority: int | None

    Notes:
        validator accepted parameters: (cls, value, values, config, field)

    """

    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_USERNAME: str | None = Field(default=None, env="REDIS_USERNAME")
    REDIS_PASSWORD: str | None = Field(default=None, env="REDIS_PASSWORD")
    REDIS_URL: RedisDsn | None = None

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("REDIS_PORT", mode="before")
    def validate_redis_port(cls, value):
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                print("REDIS_PORT environment variable must be an integer")
                raise ValueError(
                    f"REDIS_PORT environment variable must be an integer, got {value}"
                )
        return value

    @field_validator("REDIS_URL", mode="before")
    def assemble_redis_url_connection(cls, value, info):
        if value is not None:
            return value
        values = info.data
        return f"redis://{values.get('REDIS_HOST')}"
