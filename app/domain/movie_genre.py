from datetime import datetime
from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.models import MovieGenre as MovieGenreModel

class MovieGenreBase(BaseModelDatabaseMixin):
    model: ClassVar[type[MovieGenreModel]] = MovieGenreModel
    
    id: Optional[int] = None
    movie_id: int
    genre_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None