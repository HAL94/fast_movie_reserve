from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.schema.reservation import Reservation, ReservationCreate
from app.schema.role import UserRoles
from app.schema.user.user_base import UserBase


router = APIRouter(prefix="/reservations")


@router.post("/hold-seat", response_model=Reservation)
async def create_held_reservation(
    data: ReservationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: UserBase = Depends(ValidateJwt(UserRoles.REGULAR_USER)),
):
    """
    Initial preservation of the seat with status HELD:
    - Role: Temporary Inventory Lock for seat selection/checkout.
    - Primary Trigger: User selects seats and proceeds to payment (starts a timer).
    - Inventory/Seat Status: Temporarily Blocked (Released upon timer expiration).

    The HELD status is focused on temporary inventory protection while the user prepares to pay.
    """
    return await Reservation.create_held(session, data, user.id)


@router.patch("/confirm-seat/{reservation_id:path}", response_model=Reservation)
async def update_reservation_confirmed(
    reservation_id: int,
    session: AsyncSession = Depends(get_async_session),
    payment_id: str = Query(
        default=None,
        description="Payment processor result id for a reservation payment",
    ),
):
    return await Reservation.update_confirmed(session, reservation_id, payment_id)

@router.patch("/no-show/{reservation_id:path}", response_model=Reservation)
async def update_reservation_no_show(
    reservation_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await Reservation.update_no_show(session, reservation_id)

@router.patch("/cancel/{reservation_id:path}", response_model=Reservation)
async def update_reservation_canceled(reservation_id: int,
                                      session: AsyncSession = Depends(get_async_session)):
    return await Reservation.update_canceled(session, reservation_id)