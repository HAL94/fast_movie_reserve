from datetime import datetime
from typing import ClassVar, Optional

from pydantic import Field
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Genre as GenreModel

class GenreBase(BaseModelDatabaseMixin):
    model: ClassVar[type[GenreModel]] = GenreModel

    id: Optional[int] = None
    title: str
    updated_at: Optional[datetime] = Field(default=datetime.now())

    class GenrePagination(PaginationFactory.create(GenreModel)):
        pass