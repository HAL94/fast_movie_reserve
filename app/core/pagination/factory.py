from abc import ABC, abstractmethod
import enum
from functools import cached_property
from typing import Any, ClassVar, Optional
from pydantic import Field, field_validator, model_validator
from sqlalchemy import Boolean, ColumnElement, DateTime, Float, Integer, asc, desc
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.core.database import Base
from app.core.exceptions import BadRequestException
from app.core.schema import AppBaseModel


class PaginationQuery(AppBaseModel, ABC):
    page: Optional[int] = Field(None, ge=1)
    size: Optional[int] = Field(None, ge=1)
    sort_by: Optional[str] = None
    filter_by: Optional[str] = None
    skip: bool = Field(
        False,
        description="If true, pagination (page and size) is skipped, and all records are fetched.",
    )

    @model_validator(mode="after")
    def validate_pagination_fields(self) -> "PaginationQuery":
        if not self.skip:
            # If skip is False, page and size must be provided
            if self.page is None:
                raise ValueError(
                    "Page is required when pagination is not skipped (skip=False)."
                )
            if self.size is None:
                raise ValueError(
                    "Size is required when pagination is not skipped (skip=False)."
                )
        else:
            # If skip is True, page and size should be None (or effectively ignored if present)
            pass

        return self

    @abstractmethod
    def sort_fields() -> list[InstrumentedAttribute]:
        pass

    @abstractmethod
    def filter_fields() -> list[ColumnElement]:
        pass


class InvalidDatetimeValue(Exception):
    def __init__(
        self, message="Type of field is datetime, value has to be in isoformat"
    ):
        super().__init__(message)
        self.message = message


class InvalidOperator(Exception):
    pass


class LogicalOperator(enum.StrEnum):
    EQ = "="
    LTE = "<="
    LT = "<"
    GTE = ">="
    GT = ">"
    NOT = "!="
    ILIKE = "~"

    def __str__(self):
        return self.value

    @classmethod
    def all_values(cls):
        return str([operator.value for operator in cls])


class FieldOperation:
    @classmethod
    def determine_operator(cls, field_str: str) -> LogicalOperator:
        if LogicalOperator.GTE in field_str:
            return LogicalOperator.GTE

        if LogicalOperator.GT in field_str:
            return LogicalOperator.GT

        if LogicalOperator.LTE in field_str:
            return LogicalOperator.LTE

        if LogicalOperator.LT in field_str:
            return LogicalOperator.LT

        if LogicalOperator.NOT in field_str:
            return LogicalOperator.NOT

        if LogicalOperator.EQ in field_str:
            return LogicalOperator.EQ

        if LogicalOperator.ILIKE in field_str:
            return LogicalOperator.ILIKE

        raise InvalidOperator

    @classmethod
    def create_sql_expression(
        cls, column: InstrumentedAttribute, operator: LogicalOperator, column_value: Any
    ) -> list[ColumnElement]:
        if operator is LogicalOperator.GTE:
            return [column >= column_value]
        if operator is LogicalOperator.GT:
            return [column > column_value]
        if operator is LogicalOperator.LTE:
            return [column <= column_value]
        if operator is LogicalOperator.LT:
            return [column < column_value]
        if operator is LogicalOperator.NOT:
            return [column != column_value]
        if operator is LogicalOperator.EQ:
            return [column == column_value]
        if operator is LogicalOperator.ILIKE:
            return [column.ilike(f"%{column_value}%")]

        raise ValueError("No suppoerted oeprations were determined")


class PaginationParser:
    @classmethod
    def split_and_clean_fields(cls, fields: Optional[str] = None) -> list[str]:
        if not fields:
            return []
        return [field.strip() for field in fields.split(",")]

    @classmethod
    def validate_field(
        cls,
        field: str,
        allowed_fields: list[str],
        error_message: str = "Sorting not allowed on field '{field}'. Allowed fields are {allowed_fields}",
    ) -> None:
        """Validates if a field is in the allowed list."""
        # print(f"validatin if {field} exist in {allowed_fields}")
        if field not in allowed_fields:
            raise BadRequestException(
                error_message.format(field=field, allowed_fields=allowed_fields)
            )

    @classmethod
    def convert_value(cls, *, value: Any, column_type: Any, field_name: str):
        """
        Convert value to appropriate type based on column type.

        :param value: String value to convert
        :param column_type: SQLAlchemy column type
        :return: Converted value
        """
        try:
            if isinstance(column_type, Integer):
                return int(value)
            if isinstance(column_type, Float):
                return float(value)
            if isinstance(column_type, Boolean):
                return bool(value)
            if isinstance(column_type, DateTime):
                from datetime import datetime

                try:
                    return datetime.fromisoformat(value)
                except Exception:
                    raise InvalidDatetimeValue(
                        message=f"Expected type of '{field_name}' is '{str(column_type).lower()}', could not parse the value '{value}'"
                    )
            return value
        except InvalidDatetimeValue as e:
            raise BadRequestException(detail=str(e))
        except Exception:
            raise ValueError(
                f"Type of field '{field_name}' is '{str(column_type).lower()}' but value passed is: '{type(value).__name__}'"
            )


class PaginationSortParser(PaginationParser):
    def _process_sort_fields(
        self, sort_by_str: str, model: Base
    ) -> list[InstrumentedAttribute]:
        """
        Process and validate sort fields.

        :param model: SQLAlchemy model class
        :return: List of sort expressions
        """
        # print(f"sort_by is: {sort_by_str}")
        sort_fields = self.split_and_clean_fields(sort_by_str)
        sort_by = []

        for field in sort_fields:
            if not field:
                continue

            clean_field = field.lstrip("-")
            is_descending = field.startswith("-")

            try:
                column = getattr(model, clean_field)
                sort_expr = desc(column) if is_descending else asc(column)
                sort_by.append(sort_expr)
            except Exception as e:
                print(f"Invalid sort field {clean_field}: {e}")

        return sort_by


class PaginationFilterParser(PaginationParser):
    def _process_filter_fields(
        self, filter_by_str: str, model: Base
    ) -> list[ColumnElement]:
        """
        Process and validate filter fields with type conversion.

        :param model: SQLAlchemy model class
        :return: List of filter expressions
        """
        filter_fields = self.split_and_clean_fields(filter_by_str)
        filter_by = []

        for pair in filter_fields:
            if not pair:
                continue

            operator: LogicalOperator = None
            try:
                operator = FieldOperation.determine_operator(pair)

                key, value = pair.split(operator.value, 1)

                column: InstrumentedAttribute = getattr(model, key)

                converted_value = self.convert_value(
                    value=value, column_type=column.type, field_name=key
                )

                sql_expr = FieldOperation.create_sql_expression(
                    column=column, operator=operator, column_value=converted_value
                )

                filter_by.extend(sql_expr)
            except InvalidOperator:
                print("Invalid oeprator passed")
            except ValueError as e:
                # print(f"Invalid filter: {pair} {operator}")
                raise BadRequestException(detail=str(e)) from e

        return filter_by


class PaginationFactory:
    @staticmethod
    def create(
        model: Base,
        /,
        *,
        exclude_sort_fields: list[str] = [],
        exclude_filter_fields: list[str] = [],
    ) -> PaginationQuery:
        filter_parser = PaginationFilterParser()
        sort_parser = PaginationSortParser()

        fields = model.columns()

        sort_fields = fields
        filter_fields = fields

        excluded_sort = set(exclude_sort_fields)
        excluded_filter = set(exclude_filter_fields)

        sortable_fields = list(sort_fields - excluded_sort)
        filterable_fields = list(filter_fields - excluded_filter)

        class CustomPaginationQuery(PaginationQuery):
            __model__: ClassVar[Base] = model

            @cached_property
            def sort_fields(self):
                return sort_parser._process_sort_fields(self.sort_by, self.__model__)

            @cached_property
            def filter_fields(self):
                return filter_parser._process_filter_fields(
                    self.filter_by, self.__model__
                )

            @field_validator("sort_by")
            @classmethod
            def validate_sort_fields(cls, v):
                if not v:
                    return v

                sort_fields = sort_parser.split_and_clean_fields(v)

                for field in sort_fields:
                    clean_field = field.lstrip("-")

                    sort_parser.validate_field(
                        field=clean_field, allowed_fields=sortable_fields
                    )

                return v

            @field_validator("filter_by")
            @classmethod
            def validate_filter_fields(cls, v):
                if not v:
                    return v
                filter_pairs = filter_parser.split_and_clean_fields(v)

                error_message = "Filtering not allowed on field '{field}'. Allowed fields are {allowed_fields}"

                for pair in filter_pairs:
                    field = None

                    try:
                        operator: LogicalOperator = FieldOperation.determine_operator(
                            pair
                        )
                        field, _ = pair.split(operator.value, 1)

                    except Exception:
                        raise ValueError(
                            f"Invalid filter operator. Passed query is '{pair}'."
                            f" Use '<field><op><value>' format where op could be: {LogicalOperator.all_values()}"
                        )

                    filter_parser.validate_field(
                        field=field,
                        allowed_fields=filterable_fields,
                        error_message=error_message,
                    )
                return v

        return CustomPaginationQuery
