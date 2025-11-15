from fastapi import APIRouter, Depends, Response

from app.core.auth.jwt import JwtAuth, ValidateJwt
from app.core.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.role import UserRoles
from app.services.user.user_auth import UserAuth
from app.services.user import UserCredentials, UserBase, SignupRequest

from app.core.schema import AppResponse


router: APIRouter = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me", response_model=AppResponse[UserBase])
async def get_current_user(
    user: UserBase = Depends(ValidateJwt()),
) -> AppResponse[UserBase]:
    return AppResponse(data=user)


@router.get("/me/admin", response_model=AppResponse[UserBase])
async def get_admin_only(
    user: UserBase = Depends(ValidateJwt(UserRoles.ADMIN)),
) -> AppResponse[UserBase]:
    return AppResponse(data=user)


@router.post("/signup", response_model=AppResponse[UserBase])
async def signup_user(
    payload: SignupRequest, session: AsyncSession = Depends(get_async_session)
) -> AppResponse[UserBase]:
    return AppResponse(data=await UserAuth.sign_up(session, payload))


@router.post("/logout", response_model=AppResponse[dict[str, bool]])
async def logout_user(response: Response) -> AppResponse[dict[str, bool]]:
    response.delete_cookie(JwtAuth.COOKIE_KEY, samesite="lax", httponly=True)
    return AppResponse(data={"success": True})


@router.post("/login", response_model=AppResponse[dict[str, str]])
async def login_user(
    credentials: UserCredentials,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
) -> AppResponse[dict[str, str]]:
    tokenization = await UserAuth.sign_in(session, credentials)
    response.set_cookie(
        key=JwtAuth.COOKIE_KEY,
        value=tokenization.signed_token,
        max_age=JwtAuth.MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    data = {"token": tokenization.token}
    return AppResponse(data=data)
