from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Seat as SeatModel

class SeatBase(BaseModelDatabaseMixin):
    """ Base domain model for Seat """
    model: ClassVar[type[SeatModel]] = SeatModel

    id: Optional[int]
    theatre_id: int
    seat_number: str
    level: str

    class SeatPagination(PaginationFactory.create(SeatModel)):
        pass
