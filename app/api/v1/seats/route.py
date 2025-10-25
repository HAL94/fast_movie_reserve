from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.session import get_async_session
from app.schema.seat import Seat


router = APIRouter(prefix="/seats")


@router.get("/{showtime_id}")
async def get_seats(
    showtime_id: int = Path(...), 
    session: AsyncSession = Depends(get_async_session),
    pagination: Seat.SeatPagination = Query(...),
):
    return await Seat.get_available_seats_by_showtime(session, showtime_id, pagination)
