from datetime import datetime
from typing import List
from sqlalchemy import VARCHAR, ForeignKey, UniqueConstraint
from app.core.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(256), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)

    # relationships
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["Role"] = relationship(back_populates="users")


class Role(Base):
    __tablename__ = "roles"

    role_name: Mapped[str] = mapped_column(VARCHAR(64), unique=True, nullable=False)
    users: Mapped[List["User"]] = relationship(back_populates="role")


class Movie(Base):
    __tablename__ = "movies"

    title: Mapped[str] = mapped_column(VARCHAR(128), unique=True, nullable=False)
    description: Mapped[str] = mapped_column()
    rating: Mapped[int] = mapped_column()
    image_url: Mapped[str] = mapped_column()

    # relationship
    movie_genre: Mapped[list["MovieGenre"]] = relationship(back_populates="movie")
    genres: Mapped[list["Genre"]] = relationship(
        secondary="movie_genres",  # Specifies the association table
        # Points to the 'movie' relationship on the Genre model
        back_populates="movies",
        viewonly=True,  # Prevents SQLAlchemy from trying to write to the secondary table directly
    )

    showtimes: Mapped[list["Showtime"]] = relationship(back_populates="movie")


class Genre(Base):
    __tablename__ = "genres"
    title: Mapped[str] = mapped_column(VARCHAR(64), unique=True, nullable=False)

    movie_genre: Mapped[list["MovieGenre"]] = relationship(back_populates="genre")
    movies: Mapped[list["Movie"]] = relationship(
        secondary="movie_genres", back_populates="genres", viewonly=True
    )


class MovieGenre(Base):
    __tablename__ = "movie_genres"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id"), nullable=False, primary_key=True
    )
    movie: Mapped[Movie] = relationship(back_populates="movie_genre")

    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id"), nullable=False, primary_key=True
    )
    genre: Mapped[Genre] = relationship(back_populates="movie_genre")


class Theatre(Base):
    __tablename__ = "theatres"

    theatre_number: Mapped[str] = mapped_column(VARCHAR(64))
    capacity: Mapped[int] = mapped_column()

    seats: Mapped[list["Seat"]] = relationship(back_populates="theatre")
    showtimes: Mapped[list["Showtime"]] = relationship(back_populates="theatre")


class Seat(Base):
    __tablename__ = "seats"

    theatre_id: Mapped[int] = mapped_column(ForeignKey("theatres.id"), nullable=False)
    theatre: Mapped[Theatre] = relationship(back_populates="seats")

    seat_number: Mapped[str] = mapped_column(VARCHAR(64))
    level: Mapped[str] = mapped_column()


class Showtime(Base):
    __tablename__ = "showtimes"

    base_ticket_cost: Mapped[float] = mapped_column()
    start_at: Mapped[datetime] = mapped_column()
    end_at: Mapped[datetime] = mapped_column()

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)
    theatre_id: Mapped[int] = mapped_column(ForeignKey("theatres.id"), nullable=False)

    movie: Mapped[Movie] = relationship(back_populates="showtimes")
    theatre: Mapped[Theatre] = relationship(back_populates="showtimes")


class Reservation(Base):
    __tablename__ = "reservations"

    show_time_id: Mapped[int] = mapped_column(
        ForeignKey("showtimes.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(64))
    is_paid: Mapped[bool] = mapped_column()
    is_refunded: Mapped[bool] = mapped_column()
    final_price: Mapped[float] = mapped_column()
    reserved_at: Mapped[datetime] = mapped_column()

    __table_args__ = (
        UniqueConstraint("show_time_id", "seat_id", name="uc_showtime_seat"),
    )
