from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfigSettings(BaseSettings):
    ENV: str = "prod"
    APP_PORT: int = 8000
    HOST: str = "localhost"


class TransitionReservationToCompleteJobSettings(BaseSettings):
    """
    After a show had ended, we will transition all its 'CONFIRMED' reservations to 'COMPLETE'.

    """

    TRANSFORM_TO_COMPLETE_INTERVAL: int = 60 * 5  # run job every 5 minutes
    OFFSET_DELAY_MINUTES: int = 5  # run job after 5 minutes of show ending


class CheckReservationConfirmedJobSettings(BaseSettings):
    """
    Settings for the job 'check_if_confirmed' which will check if a reservation is confirmed after offset delay
    if the user have confirmed their reservation by payment within this offset time, then it will be CONFIRMED
    """

    HELD_STATUS_TIMER: int = 60


class RedisSettings(BaseSettings):
    REDIS_SERVER: str
    CELERY_RESULT_BACKEND: str


class RabbitmqSettings(BaseSettings):
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    CELERY_BROKER_URL: str


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
    SECRET_COOKIE_KEY: str = (
        "a356258a081495d33581a3aeb850666083cf6009ae29021e7201f9199e6db750"
    )


class Settings(
    PostgresSettings,
    AppConfigSettings,
    RedisSettings,
    RabbitmqSettings,
    NotificationSettings,
    JwtSettings,
    CookieSettings,
    CheckReservationConfirmedJobSettings,
    TransitionReservationToCompleteJobSettings,
):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()


def get_settings() -> Settings:
    global settings
    if settings is None:
        settings = Settings()
    return settings
