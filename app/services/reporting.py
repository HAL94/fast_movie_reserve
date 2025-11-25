from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.movie import MovieBase
from app.domain.reservation import ReservationBase
from app.domain.showtime import ShowtimeBase

from app.dto.reporting import RevenueRecord, RevenueType


class Reporting:
    @classmethod
    async def get_revenue(
        cls, session: AsyncSession, type: RevenueType = RevenueType.COMPLETE
    ) -> list[RevenueRecord]:
        try:
            if type == RevenueType.COMPLETE:
                reservation_status = ReservationBase.Status.COMPLETE
            elif type == RevenueType.POTENTIAL:
                reservation_status = ReservationBase.Status.CONFIRMED
            else:
                raise ValueError("Unknown revenue type")

            query = (
                select(
                    MovieBase.model.title,
                    MovieBase.model.id,
                    func.sum(ReservationBase.model.final_price).label(
                        "revenue"
                    ),
                    func.count(ReservationBase.model.id).label("sold_tickets"),
                )
                .join(
                    ShowtimeBase.model,
                    ShowtimeBase.model.movie_id == MovieBase.model.id,
                )
                .join(
                    ReservationBase.model,
                    ReservationBase.model.show_time_id == ShowtimeBase.model.id,
                )
                .where(
                    ReservationBase.model.status == reservation_status,
                    ReservationBase.model.is_paid,
                )
                .group_by(MovieBase.model.title, MovieBase.model.id)
                .order_by(text("revenue DESC"))
            )

            result = await session.execute(query)

            report_revenue_potential = result.fetchall()

            revenue_records = []
            for report_tuple in report_revenue_potential:
                movie_title, movie_id, movie_revenue, tickets_sold = report_tuple
                revenue_records.append(
                    RevenueRecord(
                        movie_title=movie_title,
                        movie_id=movie_id,
                        movie_revenue=movie_revenue,
                        tickets_sold=tickets_sold,
                    )
                )

            return revenue_records

        except Exception as e:
            raise e
