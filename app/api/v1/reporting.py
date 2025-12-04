from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import UserRoles
from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.core.schema import AppResponse
from app.dto.reporting import RevenueRecord, RevenueType
from app.services.reporting import Reporting


reporting_router = APIRouter(prefix="/reporting", tags=["Reporting"])


@reporting_router.get(
    "/revenue",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    response_model=AppResponse[list[RevenueRecord]],
)
async def get_potential_revenue(
    session: AsyncSession = Depends(get_async_session),
    type: RevenueType = Query(default=RevenueType.REALIZED)
) -> AppResponse[list[RevenueRecord]]:
    """Get report for either potential or realized revenue"""
    reporting_result = await Reporting.get_revenue(session, type)
    return AppResponse.create_response(reporting_result)