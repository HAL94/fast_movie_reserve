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


class Settings(
    PostgresSettings, AppConfigSettings, RedisSettings, NotificationSettings
):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()


def get_settings() -> Settings:
    global settings
    if settings is None:
        settings = Settings()
    return settings
