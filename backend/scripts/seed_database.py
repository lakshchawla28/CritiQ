import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'popcult_project.settings')
django.setup()

from apps.authentication.models import User
from apps.social.models import Achievement
from utils.tmdb_client import TMDbClient

def seed_achievements():
    achievements = [
        {
            'name': 'First Steps',
            'description': 'Watch your first movie',
            'icon': '🎬',
            'criteria': {'movies_watched': 1},
            'category': 'watching',
            'rarity': 'common',
            'points': 10
        },
        {
            'name': 'Movie Buff',
            'description': 'Watch 50 movies',
            'icon': '🍿',
            'criteria': {'movies_watched': 50},
            'category': 'watching',
            'rarity': 'rare',
            'points': 50
        },
        {
            'name': 'Critic',
            'description': 'Write 10 reviews',
            'icon': '✍️',
            'criteria': {'reviews_written': 10},
            'category': 'reviewing',
            'rarity': 'common',
            'points': 25
        },
        # Add more achievements...
    ]
    
    for ach_data in achievements:
        Achievement.objects.get_or_create(
            name=ach_data['name'],
            defaults=ach_data
        )
    
    print(f"Created {len(achievements)} achievements")

def seed_popular_movies():
    client = TMDbClient()
    data = client.get_popular_movies()
    
    for movie_data in data.get('results', [])[:20]:
        client.cache_movie(movie_data['id'])
    
    print("Seeded 20 popular movies")

if __name__ == '__main__':
    print("Starting database seeding...")
    seed_achievements()
    seed_popular_movies()
    print("Seeding complete!")