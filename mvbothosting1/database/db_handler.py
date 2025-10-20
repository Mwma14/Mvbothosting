# database/db_handler.py

import json
import os
from typing import List, Dict, Any, Optional
import uuid # Import uuid

# Define file paths
DB_DIR = os.path.dirname(__file__)
MOVIES_DB_PATH = os.path.join(DB_DIR, "movies_db.json")
SERIES_DB_PATH = os.path.join(DB_DIR, "series_db.json")

# Ensure database files exist
def initialize_databases():
    if not os.path.exists(MOVIES_DB_PATH):
        with open(MOVIES_DB_PATH, 'w') as f:
            json.dump([], f)
    if not os.path.exists(SERIES_DB_PATH):
        with open(SERIES_DB_PATH, 'w') as f:
            json.dump([], f)

def load_data(db_path: str) -> List[Dict[str, Any]]:
    """Loads data from a JSON file."""
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(db_path: str, data: List[Dict[str, Any]]):
    """Saves data to a JSON file."""
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- Movie Functions ---
def get_all_movies() -> List[Dict[str, Any]]:
    return load_data(MOVIES_DB_PATH)

def add_movie(movie_data: Dict[str, Any]):
    movies = get_all_movies()
    # Ensure ID is always set for new items
    if "id" not in movie_data:
        movie_data["id"] = str(uuid.uuid4())
    movies.append(movie_data)
    save_data(MOVIES_DB_PATH, movies)

def find_movie_by_id(movie_id: str) -> Optional[Dict[str, Any]]:
    return next((m for m in get_all_movies() if m.get("id") == movie_id), None)

def update_movie(movie_id: str, new_data: Dict[str, Any]) -> bool:
    movies = get_all_movies()
    for i, movie in enumerate(movies):
        if movie.get("id") == movie_id:
            movies[i].update(new_data)
            save_data(MOVIES_DB_PATH, movies)
            return True
    return False

def delete_movie_by_id(movie_id: str) -> bool:
    movies = get_all_movies()
    initial_len = len(movies)
    movies = [m for m in movies if m.get("id") != movie_id]
    if len(movies) < initial_len:
        save_data(MOVIES_DB_PATH, movies)
        return True
    return False

# --- Series Functions ---
def get_all_series() -> List[Dict[str, Any]]:
    return load_data(SERIES_DB_PATH)

def add_series(series_data: Dict[str, Any]):
    series = get_all_series()
    # Ensure ID is always set for new items
    if "id" not in series_data:
        series_data["id"] = str(uuid.uuid4())
    series.append(series_data)
    save_data(SERIES_DB_PATH, series)
    
def find_series_by_id(series_id: str) -> Optional[Dict[str, Any]]:
    return next((s for s in get_all_series() if s.get("id") == series_id), None)

def update_series(series_id: str, new_data: Dict[str, Any]) -> bool:
    all_series = get_all_series()
    for i, series in enumerate(all_series):
        if series.get("id") == series_id:
            all_series[i].update(new_data)
            save_data(SERIES_DB_PATH, all_series)
            return True
    return False

def delete_series_by_id(series_id: str) -> bool:
    all_series = get_all_series()
    initial_len = len(all_series)
    all_series = [s for s in all_series if s.get("id") != series_id]
    if len(all_series) < initial_len:
        save_data(SERIES_DB_PATH, all_series)
        return True
    return False

# --- Utility Functions ---
def get_all_unique_years() -> List[int]:
    movies, series = get_all_movies(), get_all_series()
    years = set()
    for item in movies + series:
        year = item.get('year')
        if isinstance(year, int):
            years.add(year)
    return sorted(list(years), reverse=True)

def get_all_unique_categories() -> List[str]:
    """Get all unique categories from both movies and series, sorted alphabetically."""
    movies, series = get_all_movies(), get_all_series()
    categories = set()
    for item in movies + series:
        if 'categories' in item and isinstance(item['categories'], list):
            for category in item['categories']:
                categories.add(category.strip())
    return sorted(list(categories))

# Initialize on import
initialize_databases()