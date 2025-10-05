from datetime import datetime
from typing import ClassVar, Optional

from pydantic import Field
from app.core.database.mixin import BaseModelDatabaseMixin
from app.models import Genre as GenreModel

class Genre(BaseModelDatabaseMixin):
    model: ClassVar[type[GenreModel]] = GenreModel

    id: Optional[int] = None
    title: str
    updated_at: Optional[datetime] = Field(default=datetime.now())