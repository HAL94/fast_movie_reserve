from typing import ClassVar, Optional
from app.core.database.mixin import BaseModelDatabaseMixin
from app.models import User as UserModel


class UserBase(BaseModelDatabaseMixin):
    model: ClassVar[type[UserModel]] = UserModel

    id: Optional[int] = None
    full_name: str
    email: str
    age: int
    role_id: int

class UserCreate(UserBase):
    hashed_password: str