from app.core.config import settings
from sqlalchemy import URL

DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.PG_USER,
    port=settings.PG_PORT,
    password=settings.PG_PW,
    host=settings.PG_SERVER,
    database=settings.PG_DB,
)
