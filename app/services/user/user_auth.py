import logging
import traceback

from fastapi import HTTPException, status
from app.core.auth.jwt import JwtAuth
from app.core.auth.schema import JwtPayload
from app.services.role import Role, UserRoles

from .user_base import UserBase, UserCreate
from .utils import SigninResult, SignupRequest, UserCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import User as UserModel
from app.core.auth.cookie import cookie_signer
from pwdlib import PasswordHash

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

password_hash = PasswordHash.recommended()


class UserAuth(UserBase):
    role: Role

    @classmethod
    async def sign_up(cls, session: AsyncSession, signup_data: SignupRequest):
        try:
            found_user = await UserBase.get_one(
                session, signup_data.email, field=cls.model.email, raise_not_found=False
            )
            if found_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This user already exists",
                )
            regular_user_role = await Role.get_one(
                session, UserRoles.REGULAR_USER, field=Role.model.role_name
            )

            created_user = await UserBase.create(
                session,
                UserCreate(
                    full_name=signup_data.full_name,
                    email=signup_data.email,
                    age=signup_data.age,
                    role_id=regular_user_role.id,
                    hashed_password=password_hash.hash(signup_data.password),
                ),
            )
            return created_user
        except Exception as e:
            logger.info(f"[UserAuth]: Failed to signup: {e} {traceback.format_exc()}")
            raise e

    @classmethod
    async def sign_in(cls, session: AsyncSession, credentials: UserCredentials):
        try:
            user_found = await cls.get_one(
                session,
                credentials.email,
                field=cls.model.email,
                options=[selectinload(UserModel.role)],
            )
            payload_data = JwtPayload(
                id=user_found.id, email=user_found.email, role=user_found.role.role_name
            )
            token = JwtAuth.encode(payload_data)

            return SigninResult(token=token, signed_token=cookie_signer.dumps(token))
        except Exception as e:
            logger.info(f"[UserAuth]: Failed to login: {e} {traceback.format_exc()}")
            raise e
