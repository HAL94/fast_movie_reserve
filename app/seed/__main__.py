import asyncio
import logging

from app.core.database.session import session_manager
from app.schema import Genre, Movie, Role, Theatre, Seat, MovieGenre, UserCreate
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
            # movies_index = ["id"]
            # await Movie.upsert_many(session, movies_data, movies_index)

            # genres_index = ["id"]
            # await Genre.upsert_many(session, genres_data, genres_index)

            # movie_genre_index = ["id", "movie_id", "genre_id"]
            # await MovieGenre.upsert_many(session, movie_genre_data, movie_genre_index)

            theatre_index = ["id"]
            await Theatre.upsert_many(session, theatres_data, theatre_index)

            seat_index = ["id"]
            await Seat.upsert_many(session, seat_data, seat_index)

            roles_index = ["id"]
            await Role.upsert_many(session, roles_data, roles_index)

            admin_user.update({"hashed_password": create_hashed_pw("123456")})
            user_index = ["id"]
            await UserCreate.upsert_one(session, admin_user, user_index)

        logging.info("Seeding has finished")
    except Exception as e:
        logger.error(f"Error occured: {e} {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(start_seeder())
