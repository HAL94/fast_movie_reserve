from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Movie as MovieModel


class Movie(BaseModelDatabaseMixin):
    model: ClassVar[type[MovieModel]] = MovieModel

    id: Optional[int]
    title: str
    description: str
    rating: int
    image_url: str

    class MoviePagination(PaginationFactory.create(MovieModel)):
        pass
