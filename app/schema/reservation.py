from datetime import datetime, timedelta
import enum
from typing import ClassVar, Optional

from pydantic import Field
from app.core.database.mixin import BaseModelDatabaseMixin
from app.core.schema import AppBaseModel
from app.models import Reservation as ReservationModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.showtime import Showtime
from app.jobs.tasks import check_if_confirmed


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
        """
        Represents the reservation lifecycle states

        HELD: User selected a seat and proceeded to payment details page, client can call to create a HELD reservation.

        PENDING: User filled his payment details and attempts to pay. client can call to create a PENDING reservation.

        CONFIRMED: User has successfully made a payment, and therefore the state can be converted to CONFIRMED.

        NO_SHOW: User did not attend the movie show.

        CANCELED: User canceled their ticket and a refund process must be started if applicable.
        """

        HELD = "HELD"
        PENDING = "PENDING"
        CONFIRMED = "CONFIRMED"
        NO_SHOW = "NO_SHOW"
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
    ) -> "Reservation":
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

            created_reservation = await cls.create(
                session, reservation_data, commit=commit, return_as_base=return_as_base
            )

            check_if_confirmed.apply_async(
                (created_reservation.id,), eta=datetime.now() + timedelta(seconds=30)
            )

            return created_reservation
        except Exception as e:
            raise e

    @classmethod
    async def update_confirmed(
        cls, session: AsyncSession, reservation_id: int, payment_id: str | None = None
    ) -> "Reservation":
        try:
            reservation_found: ReservationModel = await cls.get_one(
                session, reservation_id, return_as_base=True
            )
            # Allowed states for changing to CONFIRM state are: HELD or PENDING
            if reservation_found.status != cls.Status.PENDING and reservation_found.status != cls.Status.HELD:
                raise ValueError("Cannot modify this reservation")
            
            if payment_id != "DUMMY_PAYMENT_ID_123":
                raise ValueError("Payment not confirmed")

            reservation_found.status = cls.Status.CONFIRMED
            reservation_found.is_paid = True
            await session.commit()
            return cls.model_validate(reservation_found.dict(), from_attributes=True)
        except Exception as e:
            raise e

    @classmethod
    async def update_no_show(
        cls, session: AsyncSession, reservation_id: int,
    ) -> "Reservation":
        try:
            reservation_found: ReservationModel = await Reservation.get_one(session, reservation_id, return_as_base=True)
            if reservation_found.status != Reservation.Status.CONFIRMED:
                raise ValueError("Cannot modify this reservation")
            reservation_found.status = Reservation.Status.NO_SHOW
            await session.commit()
            return cls.model_validate(reservation_found.dict(), from_attributes=True)
        except Exception as e:
            raise e
    
    @classmethod
    async def update_canceled(
        cls, session: AsyncSession, reservation_id: int
    ):
        try:
            reservation_found: ReservationModel = await Reservation.get_one(session, reservation_id, return_as_base=True)
            if reservation_found.status != Reservation.Status.CONFIRMED:
                raise ValueError("Only confirmed statuses can be canceled")
            
            reservation_found.status = Reservation.Status.CANCELED
            await session.commit()
            return cls.model_validate(reservation_found.dict(), from_attributes=True)
        except Exception as e:
            raise e