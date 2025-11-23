from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import UserRoles
from app.core.auth.jwt import ValidateJwt
from app.core.database.session import get_async_session
from app.core.schema import AppResponse
from app.dto.reporting import PotentialRevenue
from app.services.reporting import Reporting


reporting_router = APIRouter(prefix="/reporting", tags=["Reporting"])


@reporting_router.get(
    "/potential-revenue",
    dependencies=[Depends(ValidateJwt(UserRoles.ADMIN))],
    response_model=AppResponse[list[PotentialRevenue]],
)
async def get_potential_revenue(
    session: AsyncSession = Depends(get_async_session),
) -> AppResponse[list[PotentialRevenue]]:
    reporting_result = await Reporting.get_potential_revenue(session)
    return AppResponse.create_response(reporting_result)
