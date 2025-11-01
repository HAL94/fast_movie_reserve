import logging
import traceback
from typing import ClassVar, Optional
from fastapi import HTTPException

from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Movie as MovieModel

from app.services.genre import Genre
from app.services.movie_genre import MovieGenre
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Movie(BaseModelDatabaseMixin):
    model: ClassVar[type[MovieModel]] = MovieModel

    id: Optional[int] = None
    title: str
    description: str
    rating: int
    image_url: str

    class MoviePagination(PaginationFactory.create(MovieModel)):
        pass


class MovieWithGenres(Movie):
    genres: list[Genre]


class MovieUpdate(Movie):
    id: Optional[int] = None
    genres: Optional[list[Genre]] = None

    @classmethod
    async def update_one(
        cls,
        session: AsyncSession,
        data: "MovieUpdate",
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
    ):
        try:
            updated_movie: MovieModel = await super().update_one(
                session,
                Movie(
                    id=data.id,
                    title=data.title,
                    description=data.description,
                    rating=data.rating,
                    image_url=data.image_url,
                ),
                where_clause=[cls.model.id == data.id],
                commit=False,
                return_as_base=True,
            )

            if not updated_movie:
                raise HTTPException(status_code=404, detail="Could not find movie")

            genre_index = [Genre.model.title]

            genres = await Genre.upsert_many(
                session, data.genres, genre_index, commit=False, return_as_base=False
            )

            updated_genres = []
            for genre in genres:
                updated_genres.append(
                    MovieGenre(
                        genre_id=genre.id,
                        movie_id=updated_movie.id,
                    )
                )

            movie_genres_where_clause = [MovieGenre.model.movie_id == updated_movie.id]
            if data.genres is not None:
                await MovieGenre.delete_many(
                    session, movie_genres_where_clause, commit=False
                )

            movie_genre_index = [MovieGenre.model.genre_id, MovieGenre.model.movie_id]
            await MovieGenre.upsert_many(
                session, updated_genres, movie_genre_index, on_conflict="do_nothing"
            )

            if commit:
                await session.commit()

            if return_as_base:
                return updated_movie

            return MovieUpdate(**updated_movie.dict(), genres=genres)

        except Exception as e:
            raise e


class MovieCreate(Movie):
    genres: Optional[list[Genre]] = None

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: "MovieCreate",
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
    ):
        try:
            created_movie: MovieModel = await super().create(
                session,
                Movie(
                    title=data.title,
                    description=data.description,
                    rating=data.rating,
                    image_url=data.image_url,
                ),
                commit=False,
                return_as_base=True,
            )

            genre_index = [Genre.model.title]
            await Genre.upsert_many(
                session,
                data.genres,
                genre_index,
                commit=False,
                on_conflict="do_nothing",
            )

            genres: list[Genre] = await Genre.get_all(
                session,
                where_clause=[Genre.model.title.in_([g.title for g in data.genres])],
            )
            
            movie_genres = []
            for genre in genres:
                movie_genres.append(
                    MovieGenre.model(movie_id=created_movie.id, genre_id=genre.id)
                )

            session.add_all(movie_genres)

            if commit:
                await session.commit()

            if return_as_base:
                return created_movie

            movie_with_genres = await MovieWithGenres.get_one(
                session, created_movie.id, options=[selectinload(cls.model.genres)]
            )

            return movie_with_genres
        except Exception as e:
            logger.info(f"Error in creating movie: {traceback.format_exc()}")
            raise e
