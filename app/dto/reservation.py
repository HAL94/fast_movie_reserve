from app.core.schema import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import Field


class ReservationCreate(BaseModel):
    show_time_id: int
    seat_id: int
    reserved_at: Optional[datetime] = Field(default=datetime.now())
    
