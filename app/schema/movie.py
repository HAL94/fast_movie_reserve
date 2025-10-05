import logging
from typing import ClassVar, Optional

from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Movie as MovieModel
from app.schema.genre import Genre
from app.schema.movie_genre import MovieGenre
from sqlalchemy.ext.asyncio import AsyncSession

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
            genres = await Genre.upsert_many(
                session, data.genres, genre_index, commit=False
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

            return cls.model_validate(
                MovieCreate(**created_movie.dict(), genres=genres), from_attributes=True
            )
        except Exception as e:
            raise e
