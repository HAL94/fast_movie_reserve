from datetime import timedelta
import logging

from celery import Celery

from app.core.config import settings

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

celery = Celery(
    "worker",
    backend=settings.REDIS_SERVER,
    broker=settings.CELERY_BROKER_URL,
    imports=["app.jobs.tasks"],
)

celery.conf.beat_schedule = {
    "check_confirmed_reservations": {
        "task": "app.jobs.tasks.complete_reservations.convert_reservations_to_complete",
        "schedule": timedelta(seconds=settings.INTERVAL),
    }
}
celery.conf.timezone = "UTC"
