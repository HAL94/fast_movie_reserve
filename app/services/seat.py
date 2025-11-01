import logging
from typing import ClassVar, Optional

from sqlalchemy import select
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Seat as SeatModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.reservation import Reservation
from app.services.showtime import Showtime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Seat(BaseModelDatabaseMixin):
    model: ClassVar[type[SeatModel]] = SeatModel

    id: Optional[int]
    theatre_id: int
    seat_number: str
    level: str

    class SeatPagination(PaginationFactory.create(SeatModel)):
        pass

    @classmethod
    async def get_available_seats_by_showtime(
        cls, session: AsyncSession, showtime_id: int, pagination: SeatPagination
    ):
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
