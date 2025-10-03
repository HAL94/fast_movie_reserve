from app.core.database.mixin import BaseModelDatabaseMixin
from typing import ClassVar, Optional
from app.models import User as UserModel

class UserBase(BaseModelDatabaseMixin):
    model: ClassVar[type[UserModel]] = UserModel

    id: Optional[int]
    full_name: str
    email: str
    age: int
    role_id: int

class UserCreate(UserBase):
    hashed_password: str
