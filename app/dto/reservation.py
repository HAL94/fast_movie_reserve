from app.core.schema import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import Field

from app.domain.reservation import (
    ReservationBase as Reservation,
    ReservationWithRelations,
)


class ReservationCreate(BaseModel):
    show_time_id: int
    seat_id: int
    reserved_at: Optional[datetime] = Field(default=datetime.now())


class ReservationShowtime(BaseModel):
    id: int
    start_at: datetime
    end_at: datetime
    movie_id: int
    theatre_id: int


class ReservationSeat(BaseModel):
    id: int
    seat_number: str
    level: str


class ReservationsListResponse(BaseModel):
    id: Optional[int] = None
    user_id: int
    status: Reservation.Status
    reserved_at: datetime
    is_paid: Optional[bool] = False  # in real world, got to make payment first.
    is_refunded: Optional[bool] = False
    final_price: Optional[float] = None

    showtime: ReservationShowtime
    seat: ReservationSeat

    @classmethod
    def from_reservation_with_relations(cls, item: ReservationWithRelations):
        return cls(
            id=item.id,
            user_id=item.user_id,
            status=item.status,
            reserved_at=item.reserved_at,
            is_paid=item.is_paid,
            is_refunded=item.is_refunded,
            final_price=item.final_price,
            showtime=ReservationShowtime(
                id=item.showtime.id,
                start_at=item.showtime.start_at,
                movie_id=item.showtime.movie_id,
                end_at=item.showtime.end_at,
                theatre_id=item.showtime.theatre_id,
            ),
            seat=ReservationSeat(
                id=item.seat.id,
                seat_number=item.seat.seat_number,
                level=item.seat.level,
            ),
        )
