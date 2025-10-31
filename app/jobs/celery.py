import logging

from celery import Celery

from app.core.config import settings

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

celery = Celery(
    "worker",
    backend=settings.REDIS_SERVER,
    broker=settings.CELERY_BROKER_URL,
    imports=["app.jobs.tasks"]
)


