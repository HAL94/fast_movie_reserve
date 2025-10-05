import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.schema.movie import Movie

logger = logging.getLogger("uvicorn.info")
logger.setLevel(logging.INFO)


router = APIRouter(prefix="/movies")


@router.get("/", dependencies=[Depends(ValidateJwt())])
async def get_movies(
    session: AsyncSession = Depends(get_async_session),
    query: Movie.MoviePagination = Query(...),
):
    return await Movie.get_all(session, pagination=query)


@router.get("/{id}", dependencies=[Depends(ValidateJwt())])
async def get_movie(
    id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await Movie.get_one(session, id)

