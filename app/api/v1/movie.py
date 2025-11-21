from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.core.pagination import PaginatedResult
from app.core.schema import AppResponse

from app.dto.movie import MovieCreateDto, MovieUpdateDto

from app.domain.movie import MovieWithGenres, MovieBase

from app.services.movie import Movie

from app.constants import UserRoles


movie_router = APIRouter(prefix="/movies", tags=["Movies"])


@movie_router.get("/", response_model=AppResponse[PaginatedResult[MovieBase]])
async def get_movies(
    session: AsyncSession = Depends(get_async_session),
    query: Movie.MoviePagination = Query(...),
) -> AppResponse[PaginatedResult[MovieBase]]:
    return AppResponse.create_response(
        data=await Movie.get_all(session, pagination=query)
    )


@movie_router.get("/{id}", response_model=AppResponse[MovieWithGenres])
async def get_movie(
    id: int,
    session: AsyncSession = Depends(get_async_session),
) -> AppResponse[MovieWithGenres]:
    return AppResponse.create_response(await Movie.get_one(session, id))


@movie_router.post(
    "/",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    response_model=AppResponse[MovieWithGenres],
)
async def add_movie(
    payload: MovieCreateDto, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[MovieWithGenres]:
    return AppResponse.create_response(await Movie.create(session, payload))


@movie_router.patch(
    "/{id}",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    response_model=AppResponse[MovieWithGenres],
)
async def update_movie(
    id: int, payload: MovieUpdateDto, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[MovieWithGenres]:
    payload.id = id
    return AppResponse.create_response(await Movie.update_one(session, payload))


@movie_router.delete(
    "/{id}",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    response_model=AppResponse[MovieBase],
)
async def delete_movie(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[MovieBase]:
    return AppResponse.create_response(await Movie.delete_one(session, id))
