from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.core.pagination import PaginatedResult
from app.core.schema import AppResponse

from app.constants import UserRoles

from app.services.showtime import Showtime

from app.dto.showtime import ShowtimeCreateDto, ShowtimeUpdateDto
from app.domain.showtime import ShowtimeBase, ShowtimeDetails


showtime_router = APIRouter(prefix="/showtimes", tags=["Showtimes"])


@showtime_router.get(
    "/latest",
    summary="Fetch many showtimes with pagination support starting from today",
    response_model=AppResponse[PaginatedResult[ShowtimeBase]],
)
async def get_showtimes_latest(
    session: AsyncSession = Depends(get_async_session),
    pagination: ShowtimeBase.Pagination = Query(...),
) -> AppResponse[PaginatedResult[ShowtimeBase]]:
    return AppResponse.create_response(
        await Showtime.get_all(
            session,
            pagination=pagination,
            where_clause=[Showtime.model.start_at >= datetime.now()],
        )
    )


@showtime_router.get(
    "/",
    summary="Fetch many showtimes with pagination support",
    response_model=AppResponse[PaginatedResult[ShowtimeBase]],
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
)
async def get_showtimes(
    session: AsyncSession = Depends(get_async_session),
    pagination: ShowtimeBase.Pagination = Query(...),
) -> AppResponse[PaginatedResult[ShowtimeBase]]:
    return AppResponse.create_response(
        await Showtime.get_all(
            session,
            pagination=pagination,
        )
    )


@showtime_router.get(
    "/{id}",
    summary="See details of a specific showtime",
    response_model=AppResponse[ShowtimeDetails],
)
async def get_showtime(
    id: int,
    session: AsyncSession = Depends(get_async_session),
) -> AppResponse[ShowtimeDetails]:
    return AppResponse.create_response(
        await Showtime.get_one_with_capacity(session, id)
    )


@showtime_router.post(
    "/",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    summary="Add a showtime",
    response_model=AppResponse[ShowtimeBase],
)
async def add_showtime(
    payload: ShowtimeCreateDto, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[ShowtimeBase]:
    return AppResponse.create_response(await Showtime.create(session, payload))


@showtime_router.patch(
    "/{id}",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    summary="Update a showtime",
    response_model=AppResponse[Showtime],
)
async def update_showtime(
    id: int, payload: ShowtimeUpdateDto, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[ShowtimeBase]:
    return AppResponse.create_response(
        await Showtime.update_one(
            session, payload, where_clause=[Showtime.model.id == id]
        )
    )


@showtime_router.delete(
    "/{id}",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    summary="Delete a showtime",
    response_model=AppResponse[ShowtimeBase],
)
async def delete_showtime(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[ShowtimeBase]:
    return AppResponse.create_response(await Showtime.delete_one(session, id))
