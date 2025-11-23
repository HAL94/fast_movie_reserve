from app.core.schema import BaseModel
from app.dto.genre import GenreDto, GenreUpdateDto
from typing import Optional


class MovieCreateDto(BaseModel):
    genres: Optional[list[GenreDto]] = []
    title: str
    description: str
    rating: int
    image_url: str


class MovieUpdateDto(BaseModel):
    id: Optional[int] = None
    genres: Optional[list[GenreUpdateDto]] = None
    title: str
    description: str
    rating: int
    image_url: str
