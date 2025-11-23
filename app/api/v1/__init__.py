from fastapi import APIRouter

from .auth import auth_router
from .movie import movie_router
from .genre import genre_router
from .showtime import showtime_router
from .seat import seat_router
from .reservation import reservation_router
from .theatre import theatre_router
from .reporting import reporting_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth_router)
v1_router.include_router(movie_router)
v1_router.include_router(genre_router)
v1_router.include_router(showtime_router)
v1_router.include_router(seat_router)
v1_router.include_router(reservation_router)
v1_router.include_router(theatre_router)
v1_router.include_router(reporting_router)


@v1_router.get("/welcome", tags=["Welcome"], description="Hello world endpoint")
def welcome():
    return {"Welcome": "to your fast movie reserve project"}
