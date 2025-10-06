from fastapi import APIRouter, Depends, Query

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.schema.genre import Genre
from app.schema.role import UserRoles
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/genres", dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))]
)


@router.get("/")
async def get_genres(
    session: AsyncSession = Depends(get_async_session),
    pagination: Genre.GenrePagination = Query(...),
):
    return await Genre.get_all(session, pagination=pagination)


@router.get("/{id}")
async def get_genre(id: int, session: AsyncSession = Depends(get_async_session)):
    return await Genre.get_one(session, id)


@router.post("/")
async def add_genre(payload: Genre, session: AsyncSession = Depends(get_async_session)):
    return await Genre.create(session, payload)


@router.patch("/{id}")
async def update_genre(
    id: int, payload: Genre, session: AsyncSession = Depends(get_async_session)
):
    payload.id = id
    return await Genre.update_one(session, payload, where_clause=[Genre.model.id == id])

@router.delete("/{id}")
async def delete_genre(
    id: int, session: AsyncSession = Depends(get_async_session)
):
    return await Genre.delete_one(session, id, field=Genre.model.id)
