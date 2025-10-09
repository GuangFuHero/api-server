from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    應用程式設定類別，使用 pydantic-settings 從環境變數或 .env 檔案讀取設定。

    注意：env_file 可能包含其他工具（如 Docker）使用的環境變數，
    Settings 類別只會讀取它需要的欄位，其餘會被忽略。
    """

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        extra="ignore",  # 忽略不在 Settings 中定義的環境變數
    )

    ENVIRONMENT: str
    APP_TITLE: str
    DATABASE_URL: str = ""
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    INSTANCE_CONNECTION_NAME: str = ""

    # PROD_SERVER_URL 可以有預設值，因為它不是敏感資訊
    PROD_SERVER_URL: str = "https://api.gf250923.org"
    DEV_SERVER_URL: str = "https://uat-api.gf250923.org"

    # LAN_SERVER_URL 如果在本地的 LAN 主機做為測試環境，可使用此 URL
    LAN_SERVER_URL: str = "http://192.168.1.107"
    SERVER_PORT: str = "8080"
    ALLOW_MODIFY_API_KEY_LIST: str = ""

    # LINE OAuth2/OIDC
    LINE_CLIENT_ID: str
    LINE_CLIENT_SECRET: str
    LINE_REDIRECT_URI: str
    LINE_SCOPES: str = "profile openid email"

    # LINE OAuth2/OIDC
    LINE_CLIENT_ID: str
    LINE_CLIENT_SECRET: str
    LINE_REDIRECT_URI: str
    LINE_SCOPES: str = "profile openid email"


# 建立一個全域的 settings 實例供整個專案引用
settings = Settings()
