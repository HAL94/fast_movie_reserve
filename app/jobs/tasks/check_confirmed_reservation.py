import asyncio
import traceback

from app.core.database import session_manager
from app.jobs.celery import celery

import logging
logger = logging.getLogger(__name__)


@celery.task
def check_if_confirmed(reservation_id: int) -> bool:
    # import here avoids circular imports issue
    from app.services.reservation import Reservation

    async def delete_session_if_not_confirmed():
        try:
            logger.info("[CheckReservationConfirmedJob]: started job...")
            async with session_manager.session() as session:
                reservation = await Reservation.get_one(session, reservation_id)
                if not reservation:
                    return False

                logger.info(
                    f"[CheckReservationConfirmedJob]: Got reservation with id: {reservation.id} with status: {reservation.status}"
                )

                if reservation.status == Reservation.Status.CONFIRMED \
                    or reservation.status == Reservation.Status.CANCELED:
                    return True

                await Reservation.delete_one(session, reservation_id)
                return False
        except Exception as e:
            logger.error(
                f"[CheckReservationConfirmedJob]: Failed to execute task for deleting session: {e} {traceback.format_exc()}"
            )

    running_loop = asyncio.get_event_loop()
    return running_loop.run_until_complete(delete_session_if_not_confirmed())
    
