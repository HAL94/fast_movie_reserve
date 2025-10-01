from typing import Callable, Any, override, Dict, Union
from sqlalchemy import Select, select, func, DateTime, Column
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

from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    DeclarativeBaseNoMeta as _DeclarativeBaseNoMeta,
)
from sqlalchemy.orm.decl_api import (
    DeclarativeAttributeIntercept as _DeclarativeAttributeIntercept,
)
from datetime import datetime


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

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )

    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

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
    async def get_one(
        cls,
        session: AsyncSession,
        val: Any,
        /,
        *,
        field: InstrumentedAttribute | str | None = None,
        where_clause: list[ColumnElement[bool]] = None,
    ):
        options = cls.get_options()

        if field is None:
            field = cls.id

        where_base = [field == val]

        if where_clause:
            where_base.extend(where_clause)

        statement: Select = cls.select_(cls).where(*where_base)

        if options:
            statement = statement.options(*options)

        result = await session.scalar(statement)

        return result
