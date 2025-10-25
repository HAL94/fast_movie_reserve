from datetime import datetime
import enum
from typing import ClassVar, Optional

from pydantic import Field
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.schema import AppBaseModel
from app.models import Reservation as ReservationModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.showtime import Showtime


class ReservationCreate(AppBaseModel):
    show_time_id: int
    seat_id: int
    reserved_at: Optional[datetime] = Field(default=datetime.now())


class Reservation(BaseModelDatabaseMixin):
    model: ClassVar[type[ReservationModel]] = ReservationModel

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
        HELD = "HELD"
        CONFIRMED = "CONFIRMED"
        PENDING = "PENDING"
        USER_NO_SHOW = "USER_NO_SHOW"
        CANCELED = "CANCELED"

    @classmethod
    async def create_held(
        cls,
        session: AsyncSession,
        data: ReservationCreate,
        user_id: int,
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
    ):
        try:
            showtime = await Showtime.get_one(session, data.show_time_id)
            reservation_data = Reservation(
                show_time_id=data.show_time_id,
                seat_id=data.seat_id,
                reserved_at=data.reserved_at,
                user_id=user_id,
                is_paid=False,
                is_refunded=False,
                status=cls.Status.HELD,
                final_price=showtime.base_ticket_cost,
            )
            return await cls.create(
                session, reservation_data, commit=commit, return_as_base=return_as_base
            )
        except Exception as e:
            raise e
