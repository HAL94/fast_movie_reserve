from enum import StrEnum
from typing import Optional
from pydantic import field_validator
from app.core.schema import BaseModel

class RevenueType(StrEnum):
    POTENTIAL = "POTENTIAL"
    COMPLETE = "COMPLETE"


class RevenueRecord(BaseModel):
    movie_title: str
    movie_revenue: float
    tickets_sold: int

    @field_validator('movie_revenue')
    @classmethod
    def movie_revenue_round(cls, v: Optional[float] = None):
        if not v:
            return v
        return round(v, 2)
