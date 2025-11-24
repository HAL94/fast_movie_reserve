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
                        Showtime.model.end_at < datetime.now() - timedelta(minutes=settings.OFFSET_DELAY_MINUTES),
                    ],
                    return_as_base=True,
                )

                logger.info(
                    f"Got some showtimes for processing: {showtimes_ready_to_process}"
                )
                if (
                    showtimes_ready_to_process is None
                    or len(showtimes_ready_to_process) == 0
                ):
                    logger.info(
                        "[CompleteReservationsJob]: Failed to process job, no show times list object was found...exiting"
                    )
                    return False

                for showtime in showtimes_ready_to_process:
                    logger.info(f"Showtime model: {showtime}")

                    reservations_to_transition: list[
                        Reservation
                    ] = await Reservation.get_all(
                        session,
                        where_clause=[
                            Reservation.model.status == Reservation.Status.CONFIRMED,
                            Reservation.model.show_time_id == showtime.id,
                        ],
                    )

                    logger.info(f"Reservations fetched: {reservations_to_transition}")

                    if not reservations_to_transition:
                        logger.info("Reservations passed are None. Exiting...")
                        return False

                    for reservation in reservations_to_transition:
                        reservation.status = Reservation.Status.COMPLETE
                        logger.info(
                            f"Reservation with showtime id: {reservation.show_time_id} has been transitioned to: {reservation.status}"
                        )

                    await Reservation.update_many_by_id(
                        session, reservations_to_transition, commit=False
                    )

                    showtime.is_processed_for_completion = True

                await session.commit()

                return True
        except Exception as e:
            logger.error(
                f"[CompleteReservationsJob]: Failed to execute task for deleting session: {e} {traceback.format_exc()}"
            )

    running_loop = asyncio.get_event_loop()
    return running_loop.run_until_complete(do_job())
