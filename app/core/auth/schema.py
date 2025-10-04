from pydantic import BaseModel

from app.schema.role import UserRoles


class JwtPayload(BaseModel):
    id: int
    email: str
    role: UserRoles