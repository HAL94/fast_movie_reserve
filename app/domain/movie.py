
from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Movie as MovieModel
from app.domain.genre import GenreBase as Genre
from sqlalchemy.orm import selectinload


class MovieBase(BaseModelDatabaseMixin):
    model: ClassVar[type[MovieModel]] = MovieModel

    id: Optional[int] = None
    title: str
    description: str
    rating: int
    image_url: str

    class MoviePagination(PaginationFactory.create(MovieModel)):
        pass

class MovieWithGenres(MovieBase):
    @classmethod
    def relations(cls):
        return [selectinload(cls.model.genres)]

    genres: list[Genre]