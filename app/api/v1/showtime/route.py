from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.services.role import UserRoles
from app.services.showtime import Showtime


router = APIRouter(prefix="/showtimes", dependencies=[Depends(ValidateJwt())], tags=["Showtimes"])


@router.get("/")
async def get_showtimes(
    session: AsyncSession = Depends(get_async_session),
    pagination: Showtime.ShowtimePagination = Query(...),
):
    return await Showtime.get_all(session, pagination=pagination)


@router.get("/{id}")
async def get_showtime(
    id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await Showtime.get_one(session, id)


@router.post("/", dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))])
async def add_showtime(
    payload: Showtime, session: AsyncSession = Depends(get_async_session)
):
    return await Showtime.create(session, payload)


@router.patch("/{id}", dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))])
async def update_showtime(
    id: int, payload: Showtime, session: AsyncSession = Depends(get_async_session)
):
    return await Showtime.update_one(
        session, payload, where_clause=[Showtime.model.id == id]
    )

@router.delete("/{id}", dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))])
async def delete_showtime(
    id: int, session: AsyncSession = Depends(get_async_session)
):
    return await Showtime.delete_one(session, id)