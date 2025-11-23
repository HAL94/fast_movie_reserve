from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.movie import MovieBase
from app.domain.reservation import ReservationBase
from app.domain.showtime import ShowtimeBase

from app.dto.reporting import PotentialRevenue


class Reporting:
    @classmethod
    async def get_potential_revenue(
        cls, session: AsyncSession
    ) -> list[PotentialRevenue]:
        try:
            query = (
                select(
                    MovieBase.model.title,
                    func.sum(ReservationBase.model.final_price).label(
                        "potential_revenue"
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
                    ReservationBase.model.status == ReservationBase.Status.CONFIRMED,
                    ReservationBase.model.is_paid,
                )
                .group_by(MovieBase.model.title)
                .order_by(text("potential_revenue DESC"))
            )

            result = await session.execute(query)

            report_revenue_potential = result.fetchall()

            revenue_records = []
            for report_tuple in report_revenue_potential:
                movie_title, movie_revenue, tickets_sold = report_tuple
                revenue_records.append(
                    PotentialRevenue(
                        movie_title=movie_title,
                        movie_revenue=movie_revenue,
                        tickets_sold=tickets_sold,
                    )
                )

            return revenue_records

        except Exception as e:
            raise e
