

from typing import Generic, TypeVar

from app.core.schema import AppBaseModel

T = TypeVar(name="T")

class PaginatedResult(AppBaseModel, Generic[T]):
    result: T
    total_records: int
    size: int
    page: int
