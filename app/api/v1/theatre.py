from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.constants import UserRoles
from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.core.pagination import PaginatedResult
from app.core.schema import AppResponse
from app.services.theatre import Theatre


theatre_router = APIRouter(prefix="/theatres", tags=["Theatre"])


@theatre_router.get(
    "/",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    summary="Get a list of all theatres available in the system",
    response_model=AppResponse[PaginatedResult[Theatre]],
)
async def get_theatres(
    session: AsyncSession = Depends(get_async_session),
    pagination: Theatre.Pagination = Query(...),
) -> AppResponse[PaginatedResult[Theatre]]:
    return AppResponse.create_response(
        await Theatre.get_all(session, pagination=pagination)
    )
