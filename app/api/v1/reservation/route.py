from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.core.pagination import PaginatedResult
from app.services.reservation import Reservation, ReservationCreate
from app.services.role import UserRoles
from app.services.user.user_base import UserBase

from app.redis import get_redis_client, RedisClient


router = APIRouter(prefix="/reservations", tags=["Reservation"])


@router.post(
    "/hold-seat",
    response_model=Reservation,
    description="""        
        Initial preservation of the seat with status HELD:

        The HELD status is focused on temporary inventory protection while the user prepares to pay.
    """,
)
async def create_held_reservation(
    data: ReservationCreate,
    session: AsyncSession = Depends(get_async_session),
    redis_client: RedisClient = Depends(get_redis_client),
    user: UserBase = Depends(ValidateJwt(UserRoles.REGULAR_USER)),
):
    """
    - Role: Temporary Inventory Lock for seat selection/checkout.
    - Primary Trigger: User selects seats and proceeds to payment (starts a timer).
    - Inventory/Seat Status: Temporarily Blocked (Released upon timer expiration).
    """
    return await Reservation.create_held(session, data, user.id, redis_client)


@router.patch(
    "/confirm-seat/{reservation_id:path}",
    response_model=Reservation,
    dependencies=[Depends(ValidateJwt(UserRoles.REGULAR_USER))],
)
async def update_reservation_confirmed(
    reservation_id: int,
    session: AsyncSession = Depends(get_async_session),
    redis_client: RedisClient = Depends(get_redis_client),
    payment_id: str = Query(
        default=None,
        description="Payment processor result id for a reservation payment",
    ),
):
    return await Reservation.update_confirmed(
        session, reservation_id, redis_client, payment_id
    )


@router.patch(
    "/no-show/{reservation_id:path}",
    response_model=Reservation,
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
)
async def update_reservation_no_show(
    reservation_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await Reservation.update_no_show(session, reservation_id)


@router.patch(
    "/cancel/{reservation_id:path}",
    response_model=Reservation,
    dependencies=[Depends(ValidateJwt(UserRoles.REGULAR_USER))],
)
async def update_reservation_canceled(
    reservation_id: int, session: AsyncSession = Depends(get_async_session)
):
    return await Reservation.update_canceled(session, reservation_id)


@router.get(
    "/",
    response_model=PaginatedResult[Reservation],
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
)
async def get_reservations(
    session: AsyncSession = Depends(get_async_session),
    pagination: Reservation.Pagination = Query(
        description="Paginate your reservations results",
    ),
):
    return await Reservation.get_all(session, pagination=pagination)
