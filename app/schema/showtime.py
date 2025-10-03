from datetime import datetime
from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.models import Showtime as ShowtimeModel


class Showtime(BaseModelDatabaseMixin):
    model: ClassVar[type[ShowtimeModel]] = ShowtimeModel

    id: Optional[int]
    base_ticket_cost: float
    start_at: datetime
    end_at: datetime

    movie_id: int
    theatre_id: int
