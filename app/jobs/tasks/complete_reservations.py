import asyncio
from datetime import datetime, timedelta
import traceback

from app.core.database import session_manager
from app.core.config import settings
from app.jobs.celery import celery

import logging

from app.services.showtime import Showtime
from app.models import Showtime as ShowtimeModel

logger = logging.getLogger(__name__)


@celery.task
def convert_reservations_to_complete() -> bool:
    """For a given show that ended, mark all confirmed reservations as COMPLETE"""

    async def do_job():
        from app.services.reservation import Reservation

        try:
            logger.info("[CompleteReservationsJob]: started job...")
            async with session_manager.session() as session:
                showtimes_ready_to_process: list[
                    ShowtimeModel
                ] = await Showtime.get_all(
                    session,
                    where_clause=[
                        Showtime.model.is_processed_for_completion == False,  # noqa: E712
                        Showtime.model.end_at
                        < datetime.now()
                        - timedelta(minutes=settings.OFFSET_DELAY_MINUTES),
                    ],
                    return_as_base=True,
                )

                logger.info(
                    f"Got {len(showtimes_ready_to_process)} showtimes for processing"
                )
                if (
                    showtimes_ready_to_process is None
                    or len(showtimes_ready_to_process) == 0
                ):
                    logger.info(
                        "[CompleteReservationsJob]: No showtimes to process...exiting"
                    )
                    return True

                showtime_ids = []
                for showtime in showtimes_ready_to_process:
                    showtime_ids.append(showtime.id)

                # Update reservation
                reservation_update_data = {
                    "status": Reservation.Status.COMPLETE,
                    "updated_at": datetime.now(),
                }
                reservation_where_clause = [
                    Reservation.model.show_time_id.in_(showtime_ids),
                    Reservation.model.status == Reservation.Status.CONFIRMED,
                ]
                await Reservation.update_many_by_whereclause(
                    session,
                    reservation_update_data,
                    reservation_where_clause,
                    commit=False,
                )

                # Update showtime
                showtime_update = {
                    "is_processed_for_completion": True,
                    "updated_at": datetime.now(),
                }
                showtime_where_clause = [Showtime.model.id.in_(showtime_ids)]
                await Showtime.update_many_by_whereclause(
                    session, showtime_update, showtime_where_clause, commit=False
                )
                await session.commit()
                return True
        except Exception as e:
            logger.error(
                f"[CompleteReservationsJob]: Failed to execute task for deleting session: {e} {traceback.format_exc()}"
            )

    running_loop = asyncio.get_event_loop()
    return running_loop.run_until_complete(do_job())
