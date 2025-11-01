from pydantic import BaseModel

from app.services import UserRoles

class JwtPayload(BaseModel):
    id: int
    email: str
    role: UserRoles