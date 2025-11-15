from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.services.role import UserRoles
from app.services.showtime import Showtime, ShowtimeDetails, ShowtimeCreate
from app.core.pagination import PaginatedResult
from app.core.schema import AppResponse

from datetime import datetime

router = APIRouter(prefix="/showtimes", tags=["Showtimes"])


@router.get(
    "/latest",
    summary="Fetch many showtimes with pagination support starting from today",
    response_model=AppResponse[PaginatedResult[Showtime]],
)
async def get_showtimes_latest(
    session: AsyncSession = Depends(get_async_session),
    pagination: Showtime.ShowtimePagination = Query(...),
) -> AppResponse[PaginatedResult[Showtime]]:
    return AppResponse.create_response(
        await Showtime.get_all(
            session,
            pagination=pagination,
            where_clause=[Showtime.model.start_at >= datetime.now()],
        )
    )


@router.get(
    "/",
    summary="Fetch many showtimes with pagination support starting from today",
    response_model=AppResponse[PaginatedResult[Showtime]],
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
)
async def get_showtimes(
    session: AsyncSession = Depends(get_async_session),
    pagination: Showtime.ShowtimePagination = Query(...),
) -> AppResponse[PaginatedResult[Showtime]]:
    return AppResponse.create_response(
        await Showtime.get_all(
            session,
            pagination=pagination,
        )
    )


@router.get(
    "/{id}",
    summary="See details of a specific showtime",
    response_model=AppResponse[ShowtimeDetails],
)
async def get_showtime(
    id: int,
    session: AsyncSession = Depends(get_async_session),
) -> AppResponse[ShowtimeDetails]:
    return AppResponse.create_response(await Showtime.get_one_with_capacity(session, id))


@router.post(
    "/",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    summary="Add a showtime",
    response_model=AppResponse[Showtime],
)
async def add_showtime(
    payload: ShowtimeCreate, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[Showtime]:
    return AppResponse.create_response(await Showtime.create(session, payload))


@router.patch(
    "/{id}",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    summary="Update a showtime",
    response_model=AppResponse[Showtime],
)
async def update_showtime(
    id: int, payload: Showtime, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[Showtime]:
    return AppResponse.create_response(
        await Showtime.update_one(
            session, payload, where_clause=[Showtime.model.id == id]
        )
    )


@router.delete(
    "/{id}",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    summary="Delete a showtime",
    response_model=AppResponse[Showtime],
)
async def delete_showtime(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[Showtime]:
    return AppResponse.create_response(await Showtime.delete_one(session, id))
