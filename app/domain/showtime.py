from datetime import datetime
from typing import ClassVar, Optional, Union
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.dto.showtime import ShowtimeCreateDto, ShowtimeUpdateDto
from app.models import Showtime as ShowtimeModel
from sqlalchemy.orm import selectinload
from pydantic import Field

from app.domain.movie import MovieBase as Movie
from app.domain.theatre import TheatreBase as Theatre


from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


class ShowtimeBase(BaseModelDatabaseMixin):
    model: ClassVar[type[ShowtimeModel]] = ShowtimeModel

    id: Optional[int] = None
    base_ticket_cost: float
    start_at: datetime
    end_at: datetime

    movie_id: int
    theatre_id: int

    class Pagination(PaginationFactory.create(ShowtimeModel)):
        pass

    @classmethod
    async def validate_showtime(
        cls, session: AsyncSession, data: Union[ShowtimeCreateDto, ShowtimeUpdateDto]
    ):
        try:
            await Theatre.exists(session, data.theatre_id, raise_not_found=True)
            await Movie.exists(session, data.movie_id, raise_not_found=True)

            showtimes: list[ShowtimeBase] = await ShowtimeBase.get_all(
                session,
                where_clause=[
                    ShowtimeBase.model.theatre_id == data.theatre_id,
                    ShowtimeBase.model.start_at <= data.end_at,
                    ShowtimeBase.model.end_at >= data.start_at,
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
