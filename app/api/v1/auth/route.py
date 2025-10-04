from fastapi import APIRouter, Depends, Response

from app.core.auth.jwt import JwtAuth, ValidateJwt
from app.core.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.role import UserRoles
from app.schema.user.user_auth import UserAuth
from app.schema.user import UserCredentials, UserBase, SignupRequest


router: APIRouter = APIRouter(prefix="/auth")


@router.get("/me")
async def get_current_user(user: UserBase = Depends(ValidateJwt())):
    return user


@router.get("/me/admin")
async def get_admin_only(user: UserBase = Depends(ValidateJwt(UserRoles.ADMIN))):
    return user


@router.post("/signup")
async def signup_user(
    payload: SignupRequest, session: AsyncSession = Depends(get_async_session)
):
    return await UserAuth.sign_up(session, payload)


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(JwtAuth.COOKIE_KEY, samesite="lax", httponly=True)
    return { "success": True }


@router.post("/login")
async def login_user(
    credentials: UserCredentials,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    tokenization = await UserAuth.sign_in(session, credentials)
    response.set_cookie(
        key=JwtAuth.COOKIE_KEY,
        value=tokenization.signed_token,
        max_age=JwtAuth.MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return {"token": tokenization.token}
