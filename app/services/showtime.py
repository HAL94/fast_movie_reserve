from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.domain.showtime import ShowtimeBase, ShowtimeDetails
from app.domain.reservation import ReservationBase as Reservation

from app.dto.showtime import ShowtimeCreateDto, ShowtimeUpdateDto

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Showtime(ShowtimeBase):
    @classmethod
    async def get_one_with_capacity(
        cls, session: AsyncSession, showtime_id: int
    ) -> ShowtimeDetails:
        found_showtime = await ShowtimeDetails.get_one(
            session,
            showtime_id,
        )

        all_confirmed_reservations = await Reservation.get_all(
            session,
            where_clause=[
                Reservation.model.show_time_id == showtime_id,
                Reservation.model.status == Reservation.Status.CONFIRMED,
            ],
        )

        current_capcity = found_showtime.theatre.capacity - len(
            all_confirmed_reservations
        )

        found_showtime.seats_available = current_capcity

        return found_showtime

    @classmethod
    async def update_one(
        cls,
        session: AsyncSession,
        data: ShowtimeUpdateDto,
        /,
        *,
        where_clause: list[ColumnElement[bool]] | None = None,
        commit: bool = True,
        return_as_base: bool = False,
    ) -> ShowtimeBase:
        try:
            await cls.validate_showtime(session, data)
            data = await super().update_one(
                session,
                data,
                where_clause=where_clause,
                commit=commit,
                return_as_base=return_as_base,
            )
            return data
        except Exception as e:
            raise e

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: ShowtimeCreateDto,
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
        exclude_relations=True,
    ) -> ShowtimeBase:
        try:
            await cls.validate_showtime(session, data)
            data = await super().create(
                session,
                data,
                commit=commit,
                return_as_base=return_as_base,
                exclude_relations=exclude_relations,
            )
            return data
        except Exception as e:
            raise e
