
from enum import StrEnum
from typing import ClassVar
from app.models import Role as RoleModel
from app.core.database.mixin import BaseModelDatabaseMixin

class UserRoles(StrEnum):
    ADMIN = "admin"
    REGULAR_USER = "regular_user"

class Role(BaseModelDatabaseMixin):
    model: ClassVar[type[RoleModel]] = RoleModel

    id: int
    role_name: str
