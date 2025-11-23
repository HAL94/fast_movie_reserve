from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Theatre as TheatreModel


class TheatreBase(BaseModelDatabaseMixin):
    model: ClassVar[type[TheatreModel]] = TheatreModel

    id: Optional[int]
    theatre_number: str
    capacity: int

    class Pagination(PaginationFactory.create(TheatreModel)):
        pass
