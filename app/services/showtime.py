from datetime import datetime, timezone
from typing import ClassVar, Optional, Union, Coroutine, Any
from typing_extensions import Self

from fastapi import HTTPException
from pydantic import model_validator, Field

from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.core.schema import AppResponse
from app.models import Showtime as ShowtimeModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import selectinload


from app.services.movie import Movie
from app.services.theatre import Theatre

from app.core.schema import AppBaseModel

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ShowtimeCreate(AppBaseModel):
    base_ticket_cost: float
    start_at: datetime
    end_at: datetime

    movie_id: int
    theatre_id: int

    @model_validator(mode="after")
    def validate_showtime_model(self) -> Self:
        logger.info(f"is start_at naive: {self.start_at.tzinfo}")
        logger.info(
            f"is datetime.now() func naive: {datetime.now().replace(tzinfo=timezone.utc)}"
        )

        if self.start_at < datetime.now().replace(tzinfo=timezone.utc):
            raise HTTPException(
                status_code=422, detail="Invalid: start_at must not be in past"
            )

        if self.start_at == self.end_at:
            raise HTTPException(
                status_code=422, detail="Invalid: start_at and end_at are matching"
            )

        if self.end_at < self.start_at:
            raise HTTPException(
                status_code=422, detail="Invalid: start_at is after end_at"
            )

        return self


class ShowtimeBase(BaseModelDatabaseMixin):
    model: ClassVar[type[ShowtimeModel]] = ShowtimeModel

    id: Optional[int] = None
    base_ticket_cost: float
    start_at: datetime
    end_at: datetime

    movie_id: int
    theatre_id: int

    class ShowtimePagination(PaginationFactory.create(ShowtimeModel)):
        pass

    @classmethod
    async def validate_showtime(cls, session: AsyncSession, data: "Showtime"):
        try:
            showtimes: list[Showtime] = await Showtime.get_all(
                session,
                where_clause=[
                    Showtime.model.theatre_id == data.theatre_id,
                    Showtime.model.start_at <= data.end_at,
                    Showtime.model.end_at >= data.start_at,
                ],
            )
            if len(showtimes) > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot schedule the showtime at theatre id: {data.theatre_id}, provided times are conflicting with other showtime(s): {showtimes}",
                )
        except Exception as e:
            raise e


class ShowtimeDetails(ShowtimeBase):
    movie_id: int = Field(exclude=True)
    theatre_id: int = Field(exclude=True)

    movie: Movie
    theatre: Theatre
    seats_available: Optional[int] = None

    @classmethod
    def relations(cls):
        return [selectinload(cls.model.movie), selectinload(cls.model.theatre)]


class Showtime(ShowtimeBase):
    @classmethod
    async def get_one_with_capacity(
        cls, session: AsyncSession, showtime_id: int
    ) -> Coroutine[Any, Any, ShowtimeDetails]:
        found_showtime = await ShowtimeDetails.get_one(
            session,
            showtime_id,
        )

        from app.services import Reservation

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
        data: Union["Showtime", dict],
        /,
        *,
        where_clause: list[ColumnElement[bool]] | None = None,
        commit: bool = True,
        return_as_base: bool = False,
    ) -> Coroutine[Any, Any, "Showtime"]:
        try:
            await cls.validate_showtime(session, data)
            data = await super().update_one(
                session,
                data,
                where_clause=where_clause,
                commit=commit,
                return_as_base=return_as_base,
            )
            return AppResponse(data=data)
        except Exception as e:
            raise e

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: "ShowtimeCreate",
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
        exclude_relations=True,
    ) -> Coroutine[Any, Any, "Showtime"]:
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
