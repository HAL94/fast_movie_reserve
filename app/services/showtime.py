from datetime import datetime
from typing import ClassVar, Optional, Union
from typing_extensions import Self

from fastapi import HTTPException
from pydantic import model_validator

from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Showtime as ShowtimeModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.orm import selectinload


from app.services.movie import Movie
from app.services.theatre import Theatre


class Showtime(BaseModelDatabaseMixin):
    model: ClassVar[type[ShowtimeModel]] = ShowtimeModel

    id: Optional[int] = None
    base_ticket_cost: float
    start_at: datetime
    end_at: datetime

    movie_id: int
    theatre_id: int

    class ShowtimePagination(PaginationFactory.create(ShowtimeModel)):
        pass

    @model_validator(mode="after")
    def validate_showtime_model(self) -> Self:
        if self.start_at == self.end_at:
            raise HTTPException(
                status_code=400, detail="Invalid: start_at and end_at are matching"
            )

        if self.end_at < self.start_at:
            raise HTTPException(
                status_code=400, detail="Invalid: start_at is after end_at"
            )

        return self

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
    ):
        try:
            await cls.validate_showtime(session, data)
            return await super().update_one(
                session,
                data,
                where_clause=where_clause,
                commit=commit,
                return_as_base=return_as_base,
            )
        except Exception as e:
            raise e

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: "Showtime",
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
        exclude_relations=True,
    ):
        try:
            await cls.validate_showtime(session, data)
            return await super().create(
                session,
                data,
                commit=commit,
                return_as_base=return_as_base,
                exclude_relations=exclude_relations,
            )
        except Exception as e:
            raise e


class ShowtimeDetails(Showtime):
    movie: Movie
    theatre: Theatre

    @classmethod
    async def get_one(
        cls,
        session: AsyncSession,
        val,
        /,
        *,
        field: InstrumentedAttribute | None = None,
        where_clause: list[ColumnElement[bool]] | None = None,
        options: list[_AbstractLoad] | None = [],
        return_as_base: bool = False,
        raise_not_found: bool = True,
    ):
        return await super().get_one(
            session,
            val,
            field=field,
            where_clause=where_clause,
            options=[*options, selectinload(cls.model.movie), selectinload(cls.model.theatre)],
            return_as_base=return_as_base,
            raise_not_found=raise_not_found
        )
