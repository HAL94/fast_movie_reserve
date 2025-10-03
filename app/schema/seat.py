from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.models import Seat as SeatModel

class Seat(BaseModelDatabaseMixin):
    model: ClassVar[type[SeatModel]] = SeatModel

    id: Optional[int]
    theatre_id: int
    seat_number: str
    level: str