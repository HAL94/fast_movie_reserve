import logging
import traceback

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyCookie
import jwt

from app.core.auth.schema import JwtPayload
from app.core.config import settings
from app.core.auth.cookie import cookie_signer
from app.core.database.session import get_async_session
from app.constants import UserRoles
from app.domain.user import UserBase

from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

type AccessToken = str


class JwtAuth:
    MAX_AGE = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    COOKIE_KEY = "ath"
    SECRET_KEY = settings.SECRET_KEY
    ALOGIRTHM = settings.ALGORITHM

    @classmethod
    def encode(cls, data: JwtPayload) -> str:
        """Encode some object with application Secret and Algorithm"""
        try:
            return jwt.encode(
                data.model_dump(), JwtAuth.SECRET_KEY, algorithm=JwtAuth.ALOGIRTHM
            )
        except Exception as e:
            logger.info(
                f"[JwtAuth]: Failed to encode data: {e} {traceback.format_exc()}"
            )
            raise e

    @classmethod
    async def validate_token(
        cls, session: AsyncSession, token: AccessToken, role: UserRoles | None = None
    ) -> UserBase:
        """Validate a JWT token and return payload"""
        unauth_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to decode token",
        )
        try:
            if not token:
                raise unauth_exc

            payload: dict = jwt.decode(
                token, JwtAuth.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            payload: JwtPayload = JwtPayload.model_validate(
                payload, from_attributes=True
            )

            if not payload.id:
                raise unauth_exc

            if role and payload.role != role:
                unauth_exc.detail = "Validation failed, missing role"
                raise unauth_exc

            user_data = await UserBase.get_one(session, payload.id)

            return user_data
        except Exception as e:
            logger.error(f"[JwtAuth]: validation failed: {e} {traceback.format_exc()}")
            raise unauth_exc


cookie = APIKeyCookie(name=JwtAuth.COOKIE_KEY)


async def get_token_cookie(request: Request) -> AccessToken:
    try:
        signed_data = await cookie(request)
        return cookie_signer.loads(signed_data, JwtAuth.MAX_AGE)
    except Exception as e:
        raise HTTPException(status_code=401) from e


class ValidateJwt:
    def __init__(self, role: UserRoles | None = None):
        self.role = role

    async def __call__(
        self,
        token: str = Depends(get_token_cookie),
        session: AsyncSession = Depends(get_async_session),
    ):
        try:
            return await JwtAuth.validate_token(session, token, self.role)
        except Exception as e:
            raise HTTPException(status_code=401) from e
