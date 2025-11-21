from app.core.schema import BaseModel
from datetime import datetime, timezone
from typing_extensions import Self
from typing import Union, Optional

from fastapi import HTTPException
from pydantic import model_validator
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ShowtimeDto(BaseModel):
    id: int
    base_ticket_cost: float
    start_at: datetime
    end_at: datetime

    movie_id: int
    theatre_id: int


class ShowtimeValidators:
    @classmethod
    def validate_showtime_model(
        cls, data: Union["ShowtimeCreateDto", "ShowtimeUpdateDto"]
    ) -> Union["ShowtimeCreateDto", "ShowtimeUpdateDto"]:
        logger.info(f"is start_at naive: {data.start_at.tzinfo}")
        logger.info(
            f"is datetime.now() func naive: {datetime.now().replace(tzinfo=timezone.utc)}"
        )

        if data.start_at < datetime.now().replace(tzinfo=timezone.utc):
            raise HTTPException(
                status_code=422, detail="Invalid: start_at must not be in past"
            )

        if data.start_at == data.end_at:
            raise HTTPException(
                status_code=422, detail="Invalid: start_at and end_at are matching"
            )

        if data.end_at < data.start_at:
            raise HTTPException(
                status_code=422, detail="Invalid: start_at is after end_at"
            )

        return data


class ShowtimeCreateDto(BaseModel):
    base_ticket_cost: float
    start_at: datetime
    end_at: datetime

    movie_id: int
    theatre_id: int

    @model_validator(mode="after")
    def validate_showtime_model(self) -> Self:
        return ShowtimeValidators.validate_showtime_model(self)


class ShowtimeUpdateDto(BaseModel):
    id: Optional[int] = None

    base_ticket_cost: float
    start_at: datetime
    end_at: datetime

    movie_id: int
    theatre_id: int

    @model_validator(mode="after")
    def validate_showtime_model(self) -> Self:
        return ShowtimeValidators.validate_showtime_model(self)
