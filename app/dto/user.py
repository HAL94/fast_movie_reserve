from app.core.schema import BaseModel


class UserCredentials(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    full_name: str
    email: str
    age: int
    password: str


class SigninResult(BaseModel):
    token: str
    signed_token: str


class UserCreate(BaseModel):
    full_name: str
    email: str
    age: int
    role_id: int
    hashed_password: str
