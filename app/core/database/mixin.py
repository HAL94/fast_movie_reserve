from abc import ABC
from typing import Any, ClassVar, Literal, Self, Union
from pydantic import BaseModel

from app.core.pagination.factory import PaginationQuery
from app.core.schema import AppBaseModel
from .base import Base
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from .utils import CreateModelRelations
from sqlalchemy.orm.strategy_options import _AbstractLoad


class BaseModelDatabaseMixin(AppBaseModel, ABC):
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
    async def create_many(
        cls,
        session: AsyncSession,
        data: Union[list[BaseModel] | list[dict]],
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
    ) -> Union[list[Self], list[Base]]:
        try:
            if not data or len(data) <= 0:
                return []

            result: list[Base] = await cls.model.create_many(
                session, data, commit=commit
            )

            if return_as_base:
                return result

            return [
                cls.model_validate(**item.dict(), from_attributes=True)
                for item in result
            ]
        except Exception as e:
            raise e

    @classmethod
    async def update_one(
        cls,
        session: AsyncSession,
        data: BaseModel | dict,
        /,
        *,
        where_clause: list[ColumnElement[bool]] | None = None,
        commit: bool = True,
        return_as_base: bool = False,
    ):
        try:
            result = await cls.model.update_one(
                session, data, where_clause=where_clause, commit=commit
            )

            if return_as_base:
                return result

            return cls.model_validate(result, from_attributes=True)
        except Exception as e:
            raise e

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        /,
        *,
        pagination: PaginationQuery | None = None,
        where_clause: list[ColumnElement[bool]] | None = None,
        order_clause: list[InstrumentedAttribute] | None = None,
        options: list[_AbstractLoad] | None = None,
        return_as_base: bool = False,
    ):
        try:
            if not pagination:
                result = await cls.model.get_all(
                    session,
                    where_clause=where_clause,
                    order_clause=order_clause,
                    options=options,
                )

                if return_as_base:
                    return result

                return [
                    cls.model_validate(item, from_attributes=True) for item in result
                ]

            where_clause = pagination.filter_fields
            order_clause = pagination.sort_fields
            page = pagination.page
            size = pagination.size

            paginated_result = await cls.model.get_many(
                session,
                page=page,
                size=size,
                where_clause=where_clause,
                order_clause=order_clause,
                options=options,
            )
            if return_as_base:
                return paginated_result

            result = paginated_result.result
            paginated_result.result = [
                cls.model_validate(item, from_attributes=True) for item in result
            ]

            return paginated_result

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
        options: list[_AbstractLoad] | None = None,
        return_as_base: bool = False,
        raise_not_found: bool = True,
    ) -> Self:
        result: Base = await cls.model.get_one(
            session, val, field=field, where_clause=where_clause, options=options
        )
        if not result and raise_not_found:
            raise HTTPException(status_code=404, detail="Not found")
        if not result:
            return None

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
        on_conflict: Literal["do_nothing", "do_update"] = "do_update",
    ) -> Union[Self | type[Base]]:
        if isinstance(data, dict):
            try:
                data = cls.model_validate(data, from_attributes=True)
            except Exception as e:
                raise e

        result = await cls.model.upsert_one(
            session, data, index_elements, commit=commit, on_conflict=on_conflict
        )

        if return_as_base:
            return result

        return cls.model_validate(result, from_attributes=True)

    @classmethod
    async def delete_one(
        cls,
        session: AsyncSession,
        val: Any,
        /,
        *,
        field: InstrumentedAttribute | None = None,
        where_clause: list[ColumnElement[bool]] = None,
        commit: bool = True,
        return_as_base: bool = False,
    ):
        try:
            result = await cls.model.delete_one(
                session, val, field=field, where_clause=where_clause, commit=commit
            )

            if return_as_base:
                return result

            return cls.model_validate(result, from_attributes=True)
        except Exception as e:
            raise e

    @classmethod
    async def delete_many(
        cls,
        session: AsyncSession,
        where_clause: list[ColumnElement[bool]] = None,
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
    ):
        try:
            result = await cls.model.delete_many(session, where_clause, commit=commit)

            if return_as_base:
                return result

            return [cls.model_validate(item, from_attributes=True) for item in result]
        except Exception as e:
            raise e

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
        on_conflict: Literal["do_nothing", "do_update"] = "do_update",
    ) -> Union[list[Self] | list[type[Base]]]:
        if not data or len(data) == 0:
            return []

        if isinstance(data[0], dict):
            try:
                data = [cls.model_validate(item, from_attributes=True) for item in data]
            except Exception as e:
                raise e

        result = await cls.model.upsert_many(
            session, data, index_elements, commit=commit, on_conflict=on_conflict
        )

        if return_as_base:
            return result

        return [cls.model_validate(item, from_attributes=True) for item in result]
