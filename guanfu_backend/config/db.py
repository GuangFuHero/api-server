from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    """Field attribute brief intro

    Args:
        default: Any
        default_factory: Callable[[], Any] | None = _Unset, (accept callable function or lambda function)
        alias: str | None = _Unset
        alias_priority: int | None

    Notes:
        validator accepted parameters: (cls, value, values, config, field)
    """

    DB_NAME: str = Field(..., env="DB_NAME")
    DB_USERNAME: str = Field(..., env="DB_USERNAME")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_PORT: int = Field(default=5432, env="DB_PORT")
    DATABASE_URL: str | None = None
    DATABASE_URL_ASYNC: str | None = None
    DB_LOG: bool = Field(default=False, env="DB_LOG")
    INSTANCE_CONNECTION_NAME: str | None = Field(
        env="INSTANCE_CONNECTION_NAME", default=None
    )

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("DB_PORT", mode="before")
    def validate_db_port(cls, value):
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                print("DB_PORT environment variable must be an integer")
                raise ValueError(
                    f"DB_PORT environment variable must be an integer, got {value}"
                )
        return value

    @field_validator("DATABASE_URL_ASYNC", mode="before")
    def assemble_db_connection_async(cls, value, info) -> str:
        if value is not None:
            return value
        values = info.data
        return f"postgresql+asyncpg://{values.get('DB_USERNAME')}:{values.get('DB_PASSWORD')}@{values.get('DB_HOST')}:{values.get('DB_PORT')}/{values.get('DB_NAME')}"

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, value, info) -> str:
        if value is not None:
            return value
        values = info.data
        return f"postgresql+psycopg2://{values.get('DB_USERNAME')}:{values.get('DB_PASSWORD')}@{values.get('DB_HOST')}:{values.get('DB_PORT')}/{values.get('DB_NAME')}"
