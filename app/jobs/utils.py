from .celery import celery

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def revoke_celery_task(task_id: str) ->  bool:
    try:
        celery.control.revoke(task_id, terminate=True)
        return True
    except Exception as e:
        logger.error(f"[JobsUtils]: Failed to revoke task with id: {task_id}, {e}")
        return False