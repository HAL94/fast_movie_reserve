from abc import ABC
from typing import ClassVar, Self
from pydantic import BaseModel
from .base import Base
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from .utils import CreateModelRelations

class BaseModelDatabaseMixin(BaseModel, ABC):
    model: ClassVar[type[Base]]

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: BaseModel,
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
        exclude_relations=False,
    ):
        try:
            if exclude_relations:
                result = await cls.model.create(session, data, commit=commit)
            else:
                handler = CreateModelRelations(model=cls.model)
                # Create the object graph with nested relations without commiting
                result: Base = await handler.create_with_relations(
                    session, data, commit=False
                )
                # Then commit if the flag is enabled
                if commit:
                    await session.commit()

            if return_as_base:
                return result
            
            return cls.model_validate(result, from_attributes=True)
        except Exception as e:
            raise e

    @classmethod
    async def get_one(
        cls,
        session: AsyncSession,
        val,
        /,
        *,
        field: InstrumentedAttribute | None = None,
        where_clause: list[ColumnElement[bool]] | None = None,
        return_as_base: bool = False,
    ) -> Self:
        result: Base = await cls.model.get_one(
            session, val, field=field, where_clause=where_clause
        )
        if not result:
            raise HTTPException(status_code=404, detail="Not found")

        if return_as_base:
            return result
        return cls.model_validate(result, from_attributes=True)
