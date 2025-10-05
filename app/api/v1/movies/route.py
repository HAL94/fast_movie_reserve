import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.schema.movie import Movie, MovieCreate
from app.schema.role import UserRoles

logger = logging.getLogger("uvicorn.info")
logger.setLevel(logging.INFO)


router = APIRouter(prefix="/movies", dependencies=[Depends(ValidateJwt())])


@router.get("/")
async def get_movies(
    session: AsyncSession = Depends(get_async_session),
    query: Movie.MoviePagination = Query(...),
):
    return await Movie.get_all(session, pagination=query)


@router.get("/{id}")
async def get_movie(
    id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await Movie.get_one(session, id)


@router.post("/", dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))])
async def add_movie(
    payload: MovieCreate, session: AsyncSession = Depends(get_async_session)
):
    return await MovieCreate.create(session, payload)
