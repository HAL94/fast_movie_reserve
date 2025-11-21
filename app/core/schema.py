from typing import Generic, Optional, TypeVar
from pydantic import AliasGenerator, BaseModel as OrigModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseModel(OrigModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(to_camel), populate_by_name=True
    )


T = TypeVar("T")


class AppResponse(BaseModel, Generic[T]):
    success: bool = Field(description="Is operation success", default=True)
    status_code: Optional[int] = Field(description="status code", default=200)
    internal_code: Optional[int] = Field(description="Internal code", default=None)
    message: str = Field(description="Message back to client", default="done")
    data: Optional[T] = None

    @classmethod
    def create_response(cls, data: T):
        return AppResponse(data=data)
