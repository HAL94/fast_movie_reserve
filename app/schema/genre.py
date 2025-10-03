from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.models import Genre as GenreModel

class Genre(BaseModelDatabaseMixin):
    model: ClassVar[type[GenreModel]] = GenreModel

    id: Optional[int]
    title: str