from datetime import datetime
import random

from app.constants import UserRoles

# --- Role Data ---
roles_data = [
    {
        "id": 1,
        "role_name": UserRoles.ADMIN,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "role_name": UserRoles.REGULAR_USER,
        "created_at": datetime.now()
    },
]

# --- User Data ---
admin_user = {
    "id": 1,
    "full_name": "System Administrator",
    "email": "admin@cinema.com",
    "hashed_password": "placeholder_hash", 
    "age": 35,
    "role_id": 1,
    "created_at": datetime.now()
}

# --- Genres Data ---
genres_data = [
    {"id": 1, "title": "Action", "updated_at": datetime.now()},
    {"id": 2, "title": "Adventure", "updated_at": datetime.now()},
    {"id": 3, "title": "Sci-Fi", "updated_at": datetime.now()},
    {"id": 4, "title": "Drama", "updated_at": datetime.now()},
    {"id": 5, "title": "Comedy", "updated_at": datetime.now()},
    {"id": 6, "title": "Horror", "updated_at": datetime.now()},
    {"id": 7, "title": "Thriller", "updated_at": datetime.now()},
    {"id": 8, "title": "Animation", "updated_at": datetime.now()},
    {"id": 9, "title": "Fantasy", "updated_at": datetime.now()},
    {"id": 10, "title": "Romance", "updated_at": datetime.now()},
]

# --- Movies Data ---
movies_data = [
    {
        "id": 1,
        "title": "Cosmic Odyssey",
        "description": "A thrilling journey through uncharted galaxies to save humanity.",
        "rating": 8,
        "image_url": "https://example.com/cosmic_odyssey.jpg",  # Assuming created_at is handled by Base, but explicit for clarity
    },
    {
        "id": 2,
        "title": "The Emerald Blade",
        "description": "An epic fantasy adventure where a lone hero must retrieve a legendary sword.",
        "rating": 9,
        "image_url": "https://example.com/emerald_blade.jpg",
    },
    {
        "id": 3,
        "title": "City of Whispers",
        "description": "A detective uncovers a dark conspiracy in a city plagued by secrets.",
        "rating": 7,
        "image_url": "https://example.com/city_of_whispers.jpg",
    },
    {
        "id": 4,
        "title": "Laughter Palace",
        "description": "A group of eccentric friends navigates the hilarious chaos of modern life.",
        "rating": 7,
        "image_url": "https://example.com/laughter_palace.jpg",
    },
    {
        "id": 5,
        "title": "Silent Shadows",
        "description": "A psychological horror film about a haunted house and its tormented past.",
        "rating": 8,
        "image_url": "https://example.com/silent_shadows.jpg",
    },
    {
        "id": 6,
        "title": "Pixel Pals",
        "description": "An animated adventure following a group of video game characters.",
        "rating": 8,
        "image_url": "https://example.com/pixel_pals.jpg",
    },
]

# --- Movies Genres Data ---

movie_genre_data = [
    {"id": 1, "movie_id": 1, "genre_id": 3, "created_at": datetime.now()},  # Sci-Fi
    {"id": 2, "movie_id": 1, "genre_id": 1, "created_at": datetime.now()},  # Action
    {"id": 3, "movie_id": 1, "genre_id": 2, "created_at": datetime.now()},  # Adventure
    # The Emerald Blade (ID 2)
    {"id": 4, "movie_id": 2, "genre_id": 9, "created_at": datetime.now()},  # Fantasy
    {"id": 5, "movie_id": 2, "genre_id": 2, "created_at": datetime.now()},  # Adventure
    {"id": 6, "movie_id": 2, "genre_id": 1, "created_at": datetime.now()},  # Action
    # City of Whispers (ID 3)
    {"id": 7, "movie_id": 3, "genre_id": 4, "created_at": datetime.now()},  # Drama
    {"id": 8, "movie_id": 3, "genre_id": 7, "created_at": datetime.now()},  # Thriller
    # Laughter Palace (ID 4)
    {"id": 9, "movie_id": 4, "genre_id": 5, "created_at": datetime.now()},  # Comedy
    {"id": 10, "movie_id": 4, "genre_id": 10, "created_at": datetime.now()},  # Romance
    # Silent Shadows (ID 5)
    {"id": 11, "movie_id": 5, "genre_id": 6, "created_at": datetime.now()},  # Horror
    {"id": 12, "movie_id": 5, "genre_id": 7, "created_at": datetime.now()},  # Thriller
    # Pixel Pals (ID 6)
    {"id": 13, "movie_id": 6, "genre_id": 8, "created_at": datetime.now()},  # Animation
    {"id": 14, "movie_id": 6, "genre_id": 5, "created_at": datetime.now()},  # Comedy
    {"id": 15, "movie_id": 6, "genre_id": 2, "created_at": datetime.now()},  # Adventure
]

# --- Theatre Data ---
theatres_data = [
    {"id": 1, "theatre_number": "A1", "capacity": 50},
    {"id": 2, "theatre_number": "B2", "capacity": 75},
    {
        "id": 3,
        "theatre_number": "C3",
        "capacity": 30,
    },
]

# --- Seat Data ---
# Generates seats for each theatre.
# Assumes 5 rows for Theatre 1 (A1), 7 for Theatre 2 (B2), 3 for Theatre 3 (C3)
# Max 10 seats per row.
seat_data = []
seat_id_counter = 1
seat_levels = [
    "Standard",
    "Standard",
    "Standard",
    "Luxury",
    "VIP",
]  # Weighted distribution

for theatre_info in theatres_data:
    theatre_id = theatre_info["id"]
    theatre_capacity = theatre_info["capacity"]

    # Determine approximate rows and seats per row for generating data
    if theatre_id == 1:  # A1, capacity 50
        num_rows = 5
        seats_per_row = 10
    elif theatre_id == 2:  # B2, capacity 75
        num_rows = 7
        seats_per_row = 11
    elif theatre_id == 3:  # C3, capacity 30
        num_rows = 3
        seats_per_row = 10

    for r_idx in range(num_rows):
        row_letter = chr(ord("A") + r_idx)  # A, B, C...
        for s_idx in range(1, seats_per_row + 1):
            level = random.choice(seat_levels)
            # Assign more VIP to smaller, premium theatres (C3)
            if theatre_id == 3:
                level = random.choice(
                    ["Luxury", "VIP", "VIP"]
                )  # More premium seats for C3

            seat_data.append(
                {
                    "id": seat_id_counter,
                    "theatre_id": theatre_id,
                    "seat_number": f"{row_letter}{s_idx}",
                    "level": level,
                }
            )
            seat_id_counter += 1
