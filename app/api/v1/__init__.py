from fastapi import APIRouter
from .auth.route import router as auth_router
from .movies.route import router as movie_router
from .genres.route import router as genre_router
from .showtime.route import router as showtime_router
from .seats.route import router as seat_router
from .reservation.route import router as reservation_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth_router)
v1_router.include_router(movie_router)
v1_router.include_router(genre_router)
v1_router.include_router(showtime_router)
v1_router.include_router(seat_router)
v1_router.include_router(reservation_router)



@v1_router.get("/welcome", tags=["Welcome"], description="Hello world endpoint")
def welcome():
    return {"Welcome": "to your fast movie reserve project"}


