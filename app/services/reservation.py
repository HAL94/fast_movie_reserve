from datetime import datetime, timedelta
from app.jobs.utils import revoke_celery_task
from app.models import Reservation as ReservationModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.showtime import ShowtimeBase as Showtime
from app.domain.reservation import ReservationBase, ReservationWithRelations
from app.jobs.tasks import check_if_confirmed
from app.redis import RedisClient

from app.dto.reservation import ReservationCreate


# Service Layer
class Reservation(ReservationBase):
    @classmethod
    async def create_held(
        cls,
        session: AsyncSession,
        data: ReservationCreate,
        user_id: int,
        redis_client: RedisClient,
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
    ) -> ReservationWithRelations:
        try:
            showtime = await Showtime.get_one(
                session,
                data.show_time_id,
                where_clause=[  # ensure not accessing a showtime in past
                    Showtime.model.start_at
                    >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                ],
            )
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

            task_result = check_if_confirmed.apply_async(
                (created_reservation.id,), eta=datetime.now() + timedelta(seconds=60)
            )

            await redis_client.set(
                cls.get_cache_key(created_reservation.id), task_result.id, ex=1800
            )
            reservation_detail = await ReservationWithRelations.get_one(
                session, created_reservation.id
            )

            return reservation_detail
        except Exception as e:
            raise e

    @classmethod
    async def update_confirmed(
        cls,
        session: AsyncSession,
        reservation_id: int,
        user_id: int,
        redis_client: RedisClient,
        payment_id: str | None = None,
    ) -> ReservationWithRelations:
        try:
            reservation_found: ReservationModel = (
                await ReservationWithRelations.get_one(
                    session,
                    reservation_id,
                    return_as_base=True,
                    where_clause=[cls.model.user_id == user_id],
                )
            )
            # Allowed states for changing to CONFIRM state are: HELD
            if reservation_found.status != cls.Status.HELD:
                raise ValueError("Cannot modify this reservation")

            if payment_id != "DUMMY_PAYMENT_ID_123":
                raise ValueError("Payment not confirmed")

            reservation_found.status = cls.Status.CONFIRMED
            reservation_found.is_paid = True

            task_id = await redis_client.get(cls.get_cache_key(reservation_found.id))

            if task_id:
                revoke_celery_task(task_id)

            await session.commit()

            return ReservationWithRelations.model_validate(
                reservation_found.dict(), from_attributes=True
            )
        except Exception as e:
            raise e

    @classmethod
    async def update_no_show(
        cls,
        session: AsyncSession,
        reservation_id: int,
    ) -> ReservationWithRelations:
        try:
            reservation_found: ReservationModel = (
                await ReservationWithRelations.get_one(
                    session, reservation_id, return_as_base=True
                )
            )
            if reservation_found.status != Reservation.Status.CONFIRMED:
                raise ValueError("Cannot modify this reservation")
            reservation_found.status = Reservation.Status.NO_SHOW
            await session.commit()

            return ReservationWithRelations.model_validate(
                reservation_found.dict(), from_attributes=True
            )
        except Exception as e:
            raise e

    @classmethod
    async def update_canceled(
        cls, session: AsyncSession, reservation_id: int, user_id: int
    ) -> ReservationWithRelations:
        try:
            reservation_found: ReservationModel = (
                await ReservationWithRelations.get_one(
                    session,
                    reservation_id,
                    return_as_base=True,
                    where_clause=[cls.model.user_id == user_id],
                )
            )
            if reservation_found.status != Reservation.Status.CONFIRMED:
                raise ValueError("Only confirmed statuses can be canceled")

            reservation_found.status = Reservation.Status.CANCELED
            await session.commit()
            return ReservationWithRelations.model_validate(
                reservation_found.dict(), from_attributes=True
            )
        except Exception as e:
            raise e
