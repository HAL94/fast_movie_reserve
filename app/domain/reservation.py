
import enum
from datetime import datetime
from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.pagination.factory import PaginationFactory
from app.models import Reservation as ReservationModel

from pydantic import Field
from app.domain.showtime import ShowtimeBase as Showtime
from app.domain.seat import SeatBase as Seat

from sqlalchemy.orm import selectinload


class ReservationBase(BaseModelDatabaseMixin):
    model: ClassVar[type[ReservationModel]] = ReservationModel

    @classmethod
    def relations(cls):
        return []

    id: Optional[int] = None
    show_time_id: int
    user_id: int
    seat_id: int
    status: "Status"
    reserved_at: datetime
    is_paid: Optional[bool] = False  # in real world, got to make payment first.
    is_refunded: Optional[bool] = False
    final_price: Optional[float] = None

    class Status(enum.StrEnum):
        """
        Represents the reservation lifecycle states

        HELD: User selected a seat and proceeded to payment details page, client can call to create a HELD reservation.

        CONFIRMED: User has successfully made a payment, and therefore the state can be converted to CONFIRMED.

        COMPLETE: The show has ended and the user attended.

        NO_SHOW: The show has ended and the user did not attend the show.

        CANCELED: User canceled their ticket and a refund process must be started if applicable.
        """

        HELD = "HELD"
        CONFIRMED = "CONFIRMED"
        COMPLETE = "COMPLETE"
        NO_SHOW = "NO_SHOW"
        CANCELED = "CANCELED"

    class Pagination(PaginationFactory.create(ReservationModel)):
        pass

    @classmethod
    def get_cache_key(cls, reservation_id: int):
        return f"reservations:{reservation_id}:task"


class ReservationWithRelations(ReservationBase):
    @classmethod
    def relations(cls):
        return [selectinload(cls.model.showtime), selectinload(cls.model.seat)]

    show_time_id: int = Field(exclude=True)
    seat_id: int = Field(exclude=True)

    showtime: Optional[Showtime] = None
    seat: Optional[Seat] = None