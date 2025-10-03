from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.models import Theatre as TheatreModel


class Theatre(BaseModelDatabaseMixin):
    model: ClassVar[type[TheatreModel]] = TheatreModel

    id: Optional[int]
    theatre_number: str
    capacity: int
