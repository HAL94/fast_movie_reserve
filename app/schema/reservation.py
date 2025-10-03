from datetime import datetime
from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.models import Reservation as ReservationModel

class Reservation(BaseModelDatabaseMixin):
    model: ClassVar[type[ReservationModel]] = ReservationModel

    id: Optional[int]
    show_time_id: int
    user_id: int
    seat_id: int
    status: str
    is_paid: bool
    is_refunded: bool
    final_price: float
    reserved_at: datetime