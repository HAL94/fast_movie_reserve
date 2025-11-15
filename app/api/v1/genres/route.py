from fastapi import APIRouter, Depends, Query

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.services.genre import Genre
from app.services.role import UserRoles
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.schema import AppResponse
from app.core.pagination import PaginatedResult


router = APIRouter(
    prefix="/genres",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    tags=["Genres"],
)


@router.get("/", response_model=AppResponse[PaginatedResult[Genre]])
async def get_genres(
    session: AsyncSession = Depends(get_async_session),
    pagination: Genre.GenrePagination = Query(...),
) -> AppResponse[PaginatedResult[Genre]]:
    return AppResponse.create_response(
        await Genre.get_all(session, pagination=pagination)
    )


@router.get("/{id}", response_model=AppResponse[Genre])
async def get_genre(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[Genre]:
    return AppResponse.create_response(await Genre.get_one(session, id))


@router.post("/", response_model=AppResponse[Genre])
async def add_genre(
    payload: Genre, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[Genre]:
    return AppResponse.create_response(await Genre.create(session, payload))


@router.patch("/{id}", response_model=AppResponse[Genre])
async def update_genre(
    id: int, payload: Genre, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[Genre]:
    payload.id = id
    return AppResponse.create_response(
        await Genre.update_one(session, payload, where_clause=[Genre.model.id == id])
    )


@router.delete("/{id}", response_model=AppResponse[Genre])
async def delete_genre(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[Genre]:
    return AppResponse.create_response(
        await Genre.delete_one(session, id, field=Genre.model.id)
    )
