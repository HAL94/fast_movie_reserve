from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfigSettings(BaseSettings):
    ENV: str = "prod"
    APP_PORT: int = 8000
    HOST: str = "localhost"


class RedisSettings(BaseSettings):
    REDIS_SERVER: str


class NotificationSettings(BaseSettings):
    EMAIL_KEY: str


class PostgresSettings(BaseSettings):
    PG_USER: str
    PG_PW: str
    PG_SERVER: str
    PG_PORT: str
    PG_DB: str

class JwtSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

class CookieSettings(BaseSettings):
    SECRET_COOKIE_KEY: str = "a356258a081495d33581a3aeb850666083cf6009ae29021e7201f9199e6db750"

class Settings(
    PostgresSettings, AppConfigSettings, RedisSettings, NotificationSettings, JwtSettings, CookieSettings
):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()


def get_settings() -> Settings:
    global settings
    if settings is None:
        settings = Settings()
    return settings
