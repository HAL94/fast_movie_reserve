from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.services.movie import Movie, MovieCreate, MovieUpdate, MovieWithGenres
from app.services.role import UserRoles
from app.core.pagination import PaginatedResult
from app.core.schema import AppResponse

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=AppResponse[PaginatedResult[Movie]])
async def get_movies(
    session: AsyncSession = Depends(get_async_session),
    query: Movie.MoviePagination = Query(...),
) -> AppResponse[PaginatedResult[Movie]]:
    return AppResponse.create_response(
        data=await Movie.get_all(session, pagination=query)
    )


@router.get("/{id}", response_model=AppResponse[MovieWithGenres])
async def get_movie(
    id: int,
    session: AsyncSession = Depends(get_async_session),
) -> AppResponse[MovieWithGenres]:
    return AppResponse.create_response(
        await MovieWithGenres.get_one(
            session, id, options=[selectinload(MovieWithGenres.model.genres)]
        )
    )


@router.post(
    "/",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    response_model=AppResponse[MovieWithGenres],
)
async def add_movie(
    payload: MovieCreate, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[MovieWithGenres]:
    return AppResponse.create_response(await Movie.create(session, payload))


@router.patch(
    "/{id}",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    response_model=AppResponse[MovieWithGenres],
)
async def update_movie(
    id: int, payload: MovieUpdate, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[MovieWithGenres]:
    payload.id = id
    return AppResponse.create_response(await Movie.update_one(session, payload))


@router.delete(
    "/{id}",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    response_model=AppResponse[Movie],
)
async def delete_movie(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[Movie]:
    return AppResponse.create_response(await Movie.delete_one(session, id))
