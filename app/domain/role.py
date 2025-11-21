from typing import ClassVar
from app.models import Role as RoleModel
from app.core.database.mixin import BaseModelDatabaseMixin

class RoleBase(BaseModelDatabaseMixin):
    model: ClassVar[type[RoleModel]] = RoleModel

    id: int
    role_name: str