from pydantic import BaseModel
from app.constants import UserRoles

class JwtPayload(BaseModel):
    id: int
    email: str
    role: UserRoles
