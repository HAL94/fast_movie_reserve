# Movie Reservation API

A FastAPI-based movie reservation system that provides endpoints for managing movies, showtimes, reservations, and more.

This project is from the roadmap.sh and can be found at here: [Movie Reservation System](https://roadmap.sh/projects/movie-reservation-system)

## 🛠️ Technologies & Tools

### Backend
- **FastAPI** - Modern, fast web framework for building APIs with Python
- **SQLAlchemy** - SQL toolkit and ORM for database interactions
- **Alembic** - Database migration tool
- **AsyncPG** - Fast PostgreSQL database client library
- **Celery** - Distributed task queue for background job processing
- **Redis** - In-memory data store used for caching and message brokering
- **Pydantic** - Data validation and settings management
- **JWT** - JSON Web Tokens for authentication
- **Resend** - Email delivery service for notifications

### Development Tools
- **uv** - Fast Python package installer and project manager
- **Uvicorn** - ASGI server for running FastAPI applications
- **Faker** - Generating fake data for testing and development

### Database
- **PostgreSQL** - Primary relational database
- **Redis** - Used for caching and message queue

## Project Structure

The application follows a clean architecture with clear separation of concerns:

```
app/
├── api/                  # API routes and endpoints
│   └── v1/               # API version 1
│       ├── auth.py       # Authentication endpoints
│       ├── genre.py      # Genre management
│       ├── movie.py      # Movie endpoints
│       ├── reporting.py  # Reporting endpoints
│       ├── reservation.py # Reservation endpoints
│       ├── seat.py       # Seat management
│       ├── showtime.py   # Showtime management
│       └── theatre.py    # Theatre management
│
├── core/                 # Core application configuration and utilities
│
├── domain/               # Domain models and business logic
│   ├── genre.py         
│   ├── movie.py
│   ├── movie_genre.py   
│   ├── reservation.py   
│   ├── role.py         
│   ├── seat.py         
│   ├── showtime.py     
│   ├── theatre.py      
│   └── user.py         
│
├── dto/                  # Data Transfer Objects
│   ├── genre.py
│   ├── movie.py
│   ├── reporting.py
│   ├── reservation.py
│   ├── showtime.py
│   └── user.py
│
├── services/             # Business logic services
│   ├── genre.py
│   ├── movie.py
│   ├── movie_genre.py
│   ├── reporting.py
│   ├── reservation.py
│   ├── role.py
│   ├── seat.py
│   ├── showtime.py
│   ├── theatre.py
│   └── user_auth.py
│
├── jobs/                 # Background tasks and scheduled jobs
│   ├── celery.py        # Celery configuration
│   ├── tasks/           # Task definitions
│   └── utils.py         # Job utilities
│
├── redis/                # Redis client and caching
│   └── client.py        # Redis client implementation
│
└── seed/                 # Database seeding
    ├── __main__.py      # Main seeding script
    └── data.py          # Seed data definitions
```

## API Layer

The API layer is organized by resource types with versioning support. Each resource has its own router in the `api/v1/` directory, handling:

- Authentication and authorization
- Movie management
- Showtime scheduling
- Seat reservations
- Theatre management
- Reporting and analytics

## Services Layer

The services layer contains the business logic for each domain entity. Services handle:

- Data validation
- Business rules enforcement
- Database operations
- Integration with external services
- Transaction management

## Domain Layer

The domain layer contains the core business entities and their relationships:

- **Movie**: Movie information and metadata
- **Showtime**: Scheduled movie screenings
- **Theatre**: Physical locations with screening rooms
- **Seat**: Individual seats in a theatre
- **Reservation**: Bookings made by users
- **User**: System users with authentication
- **Role**: User roles and permissions

## Data Transfer Objects (DTOs)

DTOs define the data structures used for API requests and responses, ensuring clean separation between internal models and external interfaces.

## Background Jobs

The system uses `Celery` for handling asynchronous tasks, there are only two tasks included in this work:
1. **Holding Seat**: When a customer attempt to reserve a seat for a show, the reservation is set to status `held` for some time (e.g. 15 minutes) until the user makes a payment to confirm their reservation. Currently hard-coded to `60` seconds for testing.

2. **Complete Reservations**: After a show had ended, a job is ran to convert all its reservations to a status of `Complete` for auditing purposes.

Further jobs could be achieved such as:
- Sending email notifications
- Processing batch operations
- Scheduled tasks (e.g., cleaning up expired reservations)
- Report generation

## Database Seeding

The seed module provides functionality to populate the database with initial data for development and testing:

- Sample movies and genres.
- Theatres and screening rooms.
- Showtimes.
- An admin user.

### Redis Client

The Redis client is configured in `app/redis/client.py` and provides:
- Serialization/deserialization
- Key management


## Docker Compose Setup

The easiest way to run the application with all its dependencies is using Docker Compose:

1. Make sure you have Docker and Docker Compose installed
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Update the `.env` file with your configuration if needed
4. Start the services:
   ```bash
   docker-compose up -d
   ```
5. The application will be available at `http://localhost:8000`
6. Access the API documentation at `http://localhost:8000/docs`

To stop the services:
```bash
docker-compose down
```

## Getting Started (Local Development)

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables (copy `.env.example` to `.env` and configure)

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Seed the database:
   ```bash
   uv run -m app.seed
   ```

5. Start the development server:
   ```bash
   uv run -m app
   ```

6. Access the API documentation at `http://localhost:8000/docs`