from typing import Callable, Any, Literal, override, Dict, Union
from sqlalchemy import Select, delete, insert, select, func, DateTime, Column, update
from sqlalchemy.sql.roles import ColumnsClauseRole, TypedColumnsClauseRole
from sqlalchemy.sql.elements import SQLCoreOperations, ColumnElement
from sqlalchemy.inspection import Inspectable
from sqlalchemy.sql._typing import _HasClauseElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.orm.attributes import InstrumentedAttribute
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm.strategy_options import _AbstractLoad


from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    DeclarativeBaseNoMeta as _DeclarativeBaseNoMeta,
)
from sqlalchemy.orm.decl_api import (
    DeclarativeAttributeIntercept as _DeclarativeAttributeIntercept,
)
from datetime import datetime

from app.core.pagination import PaginatedResult


class DeclarativeBaseNoMeta(_DeclarativeBaseNoMeta):
    pass


"""

TL;DR, this will allow you to write select statements as follows:
MyModel.select_(...)

instead of:

from sqlalchemy import select
select(MyModel)

Why So Many Types?
SQLAlchemy's select() function is incredibly flexible - 
it accepts columns, expressions, functions, entire tables, and more. 
This tuple tries to capture all the valid possibilities while maintaining type safety.

1. TypedColumnsClauseRole[Any]
What it is: Represents database columns that have specific type information
Example: When you define User.name: str, this type tracks that it's a string column
Use case: select(User.name) where SQLAlchemy knows name returns strings

2. ColumnsClauseRole
What it is: Generic database columns without specific type info
Example: Raw column references or dynamically created columns
Use case: select(column('some_column')) where type isn't predetermined

3. SQLCoreOperations[Any]
What it is: SQL operations and expressions (functions, calculations, etc.)
Example: func.count(), User.age + 1, case() statements
Use case: select(func.count(User.id)) - SQL functions and computed values

4. Inspectable[_HasClauseElement[Any]]
What it is: Objects that can be "inspected" to extract SQL elements
Example: Table objects, mapped classes
Use case: select(User) - passing the entire model class

5. _HasClauseElement[Any]
What it is: Objects that contain or can produce SQL clause elements
Example: Hybrid properties, custom SQL expressions
Use case: Custom properties that generate SQL when accessed
"""


class DeclarativeAttributeIntercept(_DeclarativeAttributeIntercept):
    @property
    def select_(
        cls,  # noqa: N805
    ) -> Callable[
        [
            tuple[
                TypedColumnsClauseRole[Any]
                | ColumnsClauseRole
                | SQLCoreOperations[Any]
                | Inspectable[_HasClauseElement[Any]]
                | _HasClauseElement[Any]
                | Any,
                ...,
            ],
            dict[str, Any],
        ],
        Select[Any],
    ]:
        return select


class Base(DeclarativeBaseNoMeta, metaclass=DeclarativeAttributeIntercept):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )

    def dict(self):
        return self.__dict__


    @override
    def __repr__(self) -> str:
        return str(self.dict())

    @classmethod
    async def count(cls, session: AsyncSession, /) -> int:
        return await session.scalar(func.count(cls.id))

    @classmethod
    def get_select_in_load(cls) -> list[Load]:
        return []

    @classmethod
    def get_options(cls) -> list[Load]:
        return cls.get_select_in_load()

    @classmethod
    def get_relationships(cls) -> Dict[str, RelationshipProperty[Any]]:
        mapper = inspect(cls)
        relations = {rel[0]: rel[1] for rel in mapper.relationships.items()}
        return relations

    @classmethod
    def get_foreign_columns(cls) -> Dict[str, Column]:
        relations = cls.get_relationships()
        foreign_cols = {}
        for rel in relations:
            relationship_property: RelationshipProperty = relations[rel]
            for fk in relationship_property.remote_side:
                fk: Column = fk
                foreign_cols[rel] = fk.name

        return foreign_cols

    @classmethod
    def columns(cls):
        return {_column.name for _column in inspect(cls).c}

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: Union[BaseModel, Dict],
        /,
        *,
        commit: bool = True,
    ):
        try:
            payload = data
            if isinstance(data, BaseModel):
                payload = data.model_dump(
                    exclude_none=True, exclude_unset=True, by_alias=False
                )

            obj: Base = cls(**payload)

            session.add(obj)

            if commit:
                await session.commit()

            return obj
        except IntegrityError as e:
            await session.rollback()

            if e.orig.sqlstate == UniqueViolationError.sqlstate:
                raise ValueError("Unique Constraint is Violated")
            elif e.orig.sqlstate == ForeignKeyViolationError.sqlstate:
                raise ValueError("Foreig Key Constraint is violated")

            raise e

    @classmethod
    async def create_many(
        cls,
        session: AsyncSession,
        data: Union[list[BaseModel], list[Dict]],
        /,
        *,
        commit: bool = True,
    ):
        try:
            if len(data) <= 0:
                return []
            payload = data
            if isinstance(data[0], BaseModel):
                payload = [
                    item.model_dump(
                        exclude_unset=True, exclude_none=True, by_alias=True
                    )
                    for item in data
                ]
            statement = insert(cls).returning(cls)
            return await session.scalars(statement, payload)
        except IntegrityError as e:
            await session.rollback()
            raise e

    @classmethod
    async def get_many(
        cls,
        session: AsyncSession,
        /,
        *,
        page: int,
        size: int,
        where_clause: list[ColumnElement[bool]] | None = None,
        order_clause: list[InstrumentedAttribute] | None = None,
        options: list[_AbstractLoad] | None = None,
    ):
        try:
            statement = select(cls)
            where_base = []

            if where_clause:
                where_base.extend(where_clause)

            statement = statement.where(*where_base)

            if order_clause:
                statement = statement.order_by(*order_clause)

            total_count = await session.scalar(
                select(func.count()).select_from(
                    select(cls).where(*where_base).subquery()
                )
            )
            base_options = cls.get_select_in_load()
            if base_options:
                statement = statement.options(*base_options)

            if options:
                statement = statement.options(*options)

            statement = statement.offset((page - 1) * size).limit(size)

            result = await session.scalars(statement)

            return PaginatedResult(
                result=result, size=size, page=page, total_records=total_count
            )
        except Exception as e:
            raise e

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        /,
        *,
        where_clause: list[ColumnElement[bool]] = None,
        order_clause: list[InstrumentedAttribute] = [],
        limit: int = 20,
        options: list[_AbstractLoad] | None = None,
    ):
        try:
            statement = select(cls)
            where_base = []

            if where_clause:
                where_base.extend(where_clause)

            statement = statement.where(*where_base)

            if order_clause:
                statement = statement.order_by(*order_clause)

            base_options = cls.get_options()

            if base_options:
                statement = statement.options(*base_options)

            if options:
                statement = statement.options(*options)

            statement = statement.limit(limit)

            return await session.scalars(statement)
        except Exception as e:
            raise e

    @classmethod
    async def get_one(
        cls,
        session: AsyncSession,
        val: Any,
        /,
        *,
        field: InstrumentedAttribute | str | None = None,
        options: list[_AbstractLoad] = None,
        where_clause: list[ColumnElement[bool]] = None,
    ):
        base_options = cls.get_options()

        if field is None:
            field = cls.id

        where_base = [field == val]

        if where_clause:
            where_base.extend(where_clause)

        statement: Select = cls.select_(cls).where(*where_base)

        if base_options:
            statement = statement.options(*base_options)

        if options:
            statement = statement.options(*options)

        result = await session.scalar(statement)

        return result

    @classmethod
    async def update_one(
        cls,
        session: AsyncSession,
        data: Union[BaseModel, dict],
        /,
        *,
        where_clause: list[ColumnElement[bool]] | None = None,
        commit: bool = True,
    ):
        if not where_clause:
            raise ValueError("must pass where_clause")

        if isinstance(data, BaseModel):
            data = data.model_dump(
                exclude_unset=True, exclude_none=True, by_alias=False
            )

        updated_model = await session.scalar(
            update(cls).values(data).filter(*where_clause).returning(cls)
        )

        if commit:
            await session.commit()

        return updated_model

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
    ):
        try:
            if field is None:
                field = cls.id

            if val is None:
                raise ValueError("Passed 'None' as 'val'")

            where_cond = [field == val]

            if where_clause:
                where_cond.extend(where_clause)

            result = await session.scalar(delete(cls).where(*where_cond).returning(cls))

            if commit:
                await session.commit()

            return result

        except IntegrityError as e:
            await session.rollback()

            if e.orig.sqlstate == UniqueViolationError.sqlstate:
                raise ValueError("Unique Constraint is Violated")
            elif e.orig.sqlstate == ForeignKeyViolationError.sqlstate:
                raise ValueError("Foreig Key Constraint is violated")

            raise e

    @classmethod
    async def delete_many(
        cls,
        session: AsyncSession,
        where_clause: list[ColumnElement],
        /,
        *,
        commit: bool = True,
    ):
        try:
            if not where_clause:
                raise ValueError("'where_cluse' must be passed")

            result = await session.scalars(
                delete(cls).where(*where_clause).returning(cls)
            )

            if commit:
                await session.commit()

            result = result.all()

            return result
        except IntegrityError as e:
            await session.rollback()
            if e.orig.sqlstate == UniqueViolationError.sqlstate:
                raise ValueError("Unique Constraint is Violated")
            elif e.orig.sqlstate == ForeignKeyViolationError.sqlstate:
                raise ValueError("Foreig Key Constraint is violated")

            raise e

    @classmethod
    async def upsert_one(
        cls,
        session: AsyncSession,
        data: BaseModel,
        index_elements: list[InstrumentedAttribute | str] | None = None,
        /,
        *,
        commit: bool = True,
        on_conflict: Literal["do_nothing", "do_update"] = "do_update",
    ):
        try:
            if not index_elements:
                index_elements = ["id"]

            data_dict = data.model_dump(exclude_none=True, by_alias=False)

            data_keys = set(data_dict.keys())
            index_keys = set(index_elements)
            missing_keys = index_keys - data_keys

            if missing_keys:
                raise ValueError(
                    f"Data must include all index elements. Missing: {missing_keys}"
                )

            if len(data_keys - index_keys) == 0:
                raise ValueError(
                    "Index elements match all data fields, upsert is invalid."
                )

            stmt = pg_insert(cls).values(data_dict)

            if on_conflict == "do_update":
                updated_columns = {
                    key: getattr(stmt.excluded, key)
                    for key in data_dict.keys()
                    if key not in index_elements
                }

                stmt = stmt.on_conflict_do_update(
                    index_elements=index_elements, set_=updated_columns
                )
            else:
                stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)

            result = await session.scalar(stmt.returning(cls))

            if commit:
                await session.commit()

            return result
        except IntegrityError as e:
            await session.rollback()

            if e.orig.sqlstate == UniqueViolationError.sqlstate:
                raise ValueError("Unique Constraint is Violated")
            elif e.orig.sqlstate == ForeignKeyViolationError.sqlstate:
                raise ValueError("Foreig Key Constraint is violated")

            raise e

    @classmethod
    async def upsert_many(
        cls,
        session: AsyncSession,
        data: list[BaseModel],
        index_elements: list[InstrumentedAttribute | str] | None = None,
        /,
        *,
        commit: bool = True,
        on_conflict: Literal["do_nothing", "do_update"] = "do_update",
    ):
        try:
            if not index_elements:
                index_elements = [cls.id]

            index_elements = [
                col.name if isinstance(col, InstrumentedAttribute) else str(col)
                for col in index_elements
            ]
            data_values = [
                item.model_dump(exclude_none=True, by_alias=False) for item in data
            ]

            data_model_fields = data[0].__class__.model_fields
            data_keys = set(data_model_fields.keys())
            index_keys = set(index_elements)

            # if all keys in data match with index_elements, then the operation is invalid
            # because there are no distinctions that could be used for the on conflict clause.
            if len(data_keys - index_keys) == 0:
                raise ValueError(
                    "Index elements match all model fields, upsert is invalid."
                )
            #  if no key in index_elements exists in data, then the operation is invalid
            missing_keys = index_keys - data_keys
            if missing_keys:
                raise ValueError(
                    f"Data passed must include the indexed_elements to handle conflicts. Missing: {missing_keys}"
                )

            stmt = pg_insert(cls).values(data_values)

            if on_conflict == "do_nothing":
                stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)
            else:
                updated_columns = {
                    key: getattr(stmt.excluded, key)
                    # Use the first data object's keys
                    for key in data_values[0].keys()
                    if key
                    not in index_elements  # Ensure index elements are not updated
                }
                stmt = stmt.on_conflict_do_update(
                    index_elements=index_elements, set_=updated_columns
                )

            updated_or_created_data = await session.scalars(
                stmt.returning(cls),
                execution_options={"populate_existing": True},
            )

            if commit:
                await session.commit()

            result = updated_or_created_data.all()

            return result
        except IntegrityError as e:
            await session.rollback()

            if e.orig.sqlstate == UniqueViolationError.sqlstate:
                raise ValueError("Unique Constraint is Violated")
            elif e.orig.sqlstate == ForeignKeyViolationError.sqlstate:
                raise ValueError("Foreig Key Constraint is violated")

            raise e
