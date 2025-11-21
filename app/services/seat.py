import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResult

from app.domain.showtime import ShowtimeBase as Showtime
from app.domain.seat import SeatBase
from app.domain.reservation import ReservationBase as Reservation


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Seat(SeatBase):
    @classmethod
    async def get_available_seats_by_showtime(
        cls,
        session: AsyncSession,
        showtime_id: int,
        pagination: SeatBase.SeatPagination,
    ) -> PaginatedResult[SeatBase]:
        showtime = await Showtime.get_one(session, showtime_id, field=Showtime.model.id)

        theatre_id = showtime.theatre_id

        booked_statuses = [
            Reservation.Status.HELD,
            Reservation.Status.CONFIRMED,
        ]

        booked_seats_subquery = (
            select(Reservation.model.seat_id)
            .where(Reservation.model.show_time_id == showtime_id)
            .where(Reservation.model.status.in_(booked_statuses))
        )
        reserved_seat_ids = await session.scalars(booked_seats_subquery)

        return await cls.get_all(
            session,
            pagination=pagination,
            where_clause=[
                Seat.model.theatre_id == theatre_id,
                Seat.model.id.not_in(reserved_seat_ids),
            ],
        )
