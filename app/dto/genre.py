from app.core.schema import BaseModel
from typing import Optional

from datetime import datetime
from pydantic import Field


class GenreDto(BaseModel):
    id: int
    title: str
    updated_at: Optional[datetime] = Field(default=datetime.now())

class GenreUpdateDto(BaseModel):
    id: Optional[int] = None
    title: str
    updated_at: Optional[datetime] = Field(default=None)
