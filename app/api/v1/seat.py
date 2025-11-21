from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.session import get_async_session

from app.services.seat import Seat

from app.core.schema import AppResponse
from app.core.pagination import PaginatedResult


seat_router = APIRouter(prefix="/seats", tags=["Seats"])


@seat_router.get("/{showtime_id}", response_model=AppResponse[PaginatedResult[Seat]])
async def get_seats(
    showtime_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
    pagination: Seat.SeatPagination = Query(...),
) -> AppResponse[PaginatedResult[Seat]]:
    result: PaginatedResult[Seat] = await Seat.get_available_seats_by_showtime(
        session, showtime_id, pagination
    )
    return AppResponse.create_response(data=result)
