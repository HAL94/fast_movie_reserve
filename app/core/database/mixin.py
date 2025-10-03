from abc import ABC
from typing import ClassVar, Self, Union
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
        exclude_relations=True,
    ) -> Union[Self | type[Base]]:
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
    ) -> Union[Self | type[Base]]:
        result: Base = await cls.model.get_one(
            session, val, field=field, where_clause=where_clause
        )
        if not result:
            raise HTTPException(status_code=404, detail="Not found")

        if return_as_base:
            return result
        return cls.model_validate(result, from_attributes=True)

    @classmethod
    async def upsert_one(
        cls,
        session: AsyncSession,
        data: Union[dict, BaseModel],
        index_elements: list[InstrumentedAttribute | str] | None = None,
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
    ) -> Union[Self | type[Base]]:
        if isinstance(data, dict):
            try:
                data = cls.model_validate(data, from_attributes=True)
            except Exception as e:
                raise e

        result = await cls.model.upsert_one(
            session, data, index_elements, commit=commit
        )

        if return_as_base:
            return result

        return cls.model_validate(result, from_attributes=True)

    @classmethod
    async def upsert_many(
        cls,
        session: AsyncSession,
        data: Union[list[dict] | list[BaseModel]],
        index_elements: list[InstrumentedAttribute | str] | None = None,
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
    ) -> Union[list[Self] | list[type[Base]]]:
        if isinstance(data[0], dict):
            try:
                data = [cls.model_validate(item, from_attributes=True) for item in data]
            except Exception as e:
                raise e

        result = await cls.model.upsert_many(
            session, data, index_elements, commit=commit
        )

        if return_as_base:
            return result

        return [cls.model_validate(item, from_attributes=True) for item in result]
