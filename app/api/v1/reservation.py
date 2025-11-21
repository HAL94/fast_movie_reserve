from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.core.pagination import PaginatedResult

from app.domain.user import UserBase

from app.services.reservation import Reservation, ReservationCreate, ReservationWithRelations

from app.constants import UserRoles

from app.redis import get_redis_client, RedisClient
from app.core.schema import AppResponse

reservation_router = APIRouter(prefix="/reservations", tags=["Reservation"])


@reservation_router.post(
    "/hold-seat",
    response_model=AppResponse[ReservationWithRelations],
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
) -> AppResponse[ReservationWithRelations]:
    """
    - Role: Temporary Inventory Lock for seat selection/checkout.
    - Primary Trigger: User selects seats and proceeds to payment (starts a timer).
    - Inventory/Seat Status: Temporarily Blocked (Released upon timer expiration).
    """
    return AppResponse.create_response(
        await Reservation.create_held(session, data, user.id, redis_client)
    )


@reservation_router.patch(
    "/confirm-seat/{reservation_id:path}",
    response_model=AppResponse[ReservationWithRelations],
)
async def update_reservation_confirmed(
    reservation_id: int,
    session: AsyncSession = Depends(get_async_session),
    redis_client: RedisClient = Depends(get_redis_client),
    user: UserBase = Depends(ValidateJwt(UserRoles.REGULAR_USER)),
    payment_id: str = Query(
        default=None,
        description="Payment processor result id for a reservation payment",
    ),
) -> AppResponse[ReservationWithRelations]:
    return AppResponse.create_response(
        await Reservation.update_confirmed(
            session, reservation_id, user.id, redis_client, payment_id
        )
    )


@reservation_router.patch(
    "/no-show/{reservation_id:path}",
    response_model=AppResponse[ReservationWithRelations],
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
)
async def update_reservation_no_show(
    reservation_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> AppResponse[ReservationWithRelations]:
    return AppResponse.create_response(
        await Reservation.update_no_show(session, reservation_id)
    )


@reservation_router.patch(
    "/cancel/{reservation_id:path}",
    response_model=AppResponse[ReservationWithRelations],
)
async def update_reservation_canceled(
    reservation_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: UserBase = Depends(ValidateJwt(UserRoles.REGULAR_USER)),
) -> AppResponse[ReservationWithRelations]:
    return AppResponse.create_response(
        await Reservation.update_canceled(session, reservation_id, user.id)
    )


@reservation_router.get(
    "/my-reservations",
    response_model=AppResponse[PaginatedResult[ReservationWithRelations]],
)
async def get_my_reservations(
    session: AsyncSession = Depends(get_async_session),
    user: UserBase = Depends(ValidateJwt(UserRoles.REGULAR_USER)),
    pagination: Reservation.Pagination = Query(
        description="Paginate reservations for a user",
    ),
) -> AppResponse[PaginatedResult[ReservationWithRelations]]:
    return AppResponse.create_response(
        await Reservation.get_all(
            session,
            pagination=pagination,
            where_clause=[Reservation.model.user_id == user.id],
        )
    )


@reservation_router.get(
    "/",
    response_model=AppResponse[PaginatedResult[ReservationWithRelations]],
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
)
async def get_reservations(
    session: AsyncSession = Depends(get_async_session),
    pagination: Reservation.Pagination = Query(
        description="Paginate your reservations results",
    ),
) -> AppResponse[PaginatedResult[ReservationWithRelations]]:
    return AppResponse.create_response(
        await Reservation.get_all(session, pagination=pagination)
    )
