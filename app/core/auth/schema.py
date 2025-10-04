from pydantic import BaseModel

from app.schema import UserRoles

class JwtPayload(BaseModel):
    id: int
    email: str
    role: UserRoles