import asyncio
import logging

from app.core.database.session import session_manager
from app.services import Genre, Movie, Role, Theatre, Seat, MovieGenre, UserCreate
from .data import (
    movies_data,
    movie_genre_data,
    seat_data,
    theatres_data,
    genres_data,
    roles_data,
    admin_user,
)
from pwdlib import PasswordHash
import traceback

password_hash = PasswordHash.recommended()
logger = logging.getLogger(__name__)

def create_hashed_pw(password: str):
    return password_hash.hash(password)


async def start_seeder():
    logger.info("seeding started...")

    try:
        async with session_manager.session() as session:
            movies_index = ["id"]
            await Movie.upsert_many(session, movies_data, movies_index)
            logger.info("Movie data is seeded")

            genres_index = ["id"]
            await Genre.upsert_many(session, genres_data, genres_index)
            logger.info("Genre data is seeded")

            movie_genre_index = ["id", "movie_id", "genre_id"]
            await MovieGenre.upsert_many(session, movie_genre_data, movie_genre_index)
            logger.info("MovieGenre data is seeded")


            theatre_index = ["id"]
            await Theatre.upsert_many(session, theatres_data, theatre_index)
            logger.info("Theatre data is seeded")


            seat_index = ["id"]
            await Seat.upsert_many(session, seat_data, seat_index)
            logger.info("Seat data is seeded")


            roles_index = ["id"]
            await Role.upsert_many(session, roles_data, roles_index)
            logger.info("Roles data is seeded")


            admin_user.update({"hashed_password": create_hashed_pw("123456")})
            user_index = ["id"]
            await UserCreate.upsert_one(session, admin_user, user_index)
            logger.info("User data is seeded")


        logger.info("Seeding has finished")
    except Exception as e:
        logger.error(f"Error occured: {e} {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(start_seeder())
