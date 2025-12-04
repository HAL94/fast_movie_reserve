from app.core.schema import BaseModel


class SeatDto(BaseModel):
    id: int
    seat_number: str
    level: str
