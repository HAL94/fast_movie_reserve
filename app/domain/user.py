from typing import ClassVar
from app.core.database.mixin import BaseModelDatabaseMixin
from app.models import User as UserModel


class UserBase(BaseModelDatabaseMixin):
    model: ClassVar[type[UserModel]] = UserModel

    id: int
    full_name: str
    email: str
    age: int
    role_id: int