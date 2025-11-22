import requests
from django.conf import settings
from apps.movies.models import Movie
from django.utils import timezone

class TMDbClient:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def search_movies(self, query, page=1):
        """Search movies by title"""
        endpoint = f"{self.base_url}/search/movie"
        params = {'query': query, 'page': page}
        response = requests.get(endpoint, headers=self.headers, params=params)
        return response.json()
    
    def get_movie_details(self, tmdb_id):
        """Get detailed movie information"""
        endpoint = f"{self.base_url}/movie/{tmdb_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()
    
    def get_popular_movies(self, page=1):
        """Get popular movies"""
        endpoint = f"{self.base_url}/movie/popular"
        params = {'page': page}
        response = requests.get(endpoint, headers=self.headers, params=params)
        return response.json()
    
    def get_upcoming_movies(self, page=1):
        """Get upcoming movies"""
        endpoint = f"{self.base_url}/movie/upcoming"
        params = {'page': page}
        response = requests.get(endpoint, headers=self.headers, params=params)
        return response.json()
    
    def discover_movies(self, genres=None, year=None, sort_by='popularity.desc', page=1):
        """Discover movies with filters"""
        endpoint = f"{self.base_url}/discover/movie"
        params = {
            'page': page,
            'sort_by': sort_by
        }
        if genres:
            params['with_genres'] = ','.join(map(str, genres))
        if year:
            params['year'] = year
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        return response.json()
    
    def cache_movie(self, tmdb_id):
        """Cache movie in local database"""
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
            # Update if outdated (older than 7 days)
            if (timezone.now() - movie.last_synced).days > 7:
                data = self.get_movie_details(tmdb_id)
                self._update_movie_from_api(movie, data)
            return movie
        except Movie.DoesNotExist:
            data = self.get_movie_details(tmdb_id)
            return self._create_movie_from_api(data)
    
    def _create_movie_from_api(self, data):
        """Create movie from API data"""
        movie = Movie.objects.create(
            tmdb_id=data['id'],
            title=data['title'],
            original_title=data.get('original_title', ''),
            overview=data.get('overview', ''),
            poster_path=data.get('poster_path', ''),
            backdrop_path=data.get('backdrop_path', ''),
            release_date=data.get('release_date'),
            runtime=data.get('runtime'),
            genres=[g['id'] for g in data.get('genres', [])],
            original_language=data.get('original_language', 'en'),
            tmdb_vote_average=data.get('vote_average', 0),
            tmdb_vote_count=data.get('vote_count', 0),
            last_synced=timezone.now()
        )
        return movie
    
    def _update_movie_from_api(self, movie, data):
        """Update existing movie with API data"""
        movie.title = data['title']
        movie.overview = data.get('overview', '')
        movie.poster_path = data.get('poster_path', '')
        movie.runtime = data.get('runtime')
        movie.tmdb_vote_average = data.get('vote_average', 0)
        movie.tmdb_vote_count = data.get('vote_count', 0)
        movie.last_synced = timezone.now()
        movie.save()
        return movie