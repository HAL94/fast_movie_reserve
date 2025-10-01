from sqlalchemy import VARCHAR
from app.core.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(256), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    age:  Mapped[int] = mapped_column(nullable=False)
