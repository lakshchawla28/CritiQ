from celery import shared_task
from utils.tmdb_client import TMDbClient
from .models import Movie
from django.utils import timezone

@shared_task
def update_popular_movies():
    """Update popular movies from TMDb"""
    client = TMDbClient()
    
    for page in range(1, 6):  # Get first 5 pages
        data = client.get_popular_movies(page=page)
        for movie_data in data.get('results', []):
            client.cache_movie(movie_data['id'])
    
    return "Popular movies updated"

@shared_task
def check_upcoming_releases():
    """Check and update upcoming movie releases"""
    client = TMDbClient()
    data = client.get_upcoming_movies()
    
    for movie_data in data.get('results', []):
        movie = client.cache_movie(movie_data['id'])
        movie.is_upcoming = True
        movie.save()
    
    return "Upcoming movies updated"

@shared_task
def sync_movie_details(tmdb_id):
    """Sync specific movie details"""
    client = TMDbClient()
    movie = client.cache_movie(tmdb_id)
    return f"Synced {movie.title}"