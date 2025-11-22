"""
Movies App Models
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
import uuid

class Movie(models.Model):
    """Movie Model - Cached from TMDb"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tmdb_id = models.IntegerField(unique=True, db_index=True)
    
    # Basic Info
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200, blank=True)
    overview = models.TextField()
    poster_path = models.CharField(max_length=200, blank=True)
    backdrop_path = models.CharField(max_length=200, blank=True)
    
    # Release Info
    release_date = models.DateField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)  # in minutes
    
    # Classification
    genres = models.JSONField(default=list)  # List of genre IDs
    original_language = models.CharField(max_length=10)
    
    # Ratings
    tmdb_vote_average = models.FloatField(default=0)
    tmdb_vote_count = models.IntegerField(default=0)
    
    # App-specific stats (cached)
    app_rating_average = models.FloatField(default=0)
    app_rating_count = models.IntegerField(default=0)
    watch_count = models.IntegerField(default=0)
    interested_count = models.IntegerField(default=0)
    
    # Status
    is_upcoming = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'movies'
        ordering = ['-release_date']
        indexes = [
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['release_date']),
            models.Index(fields=['is_upcoming']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'N/A'})"


class UserMovieInteraction(models.Model):
    """Track user interactions with movies"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_interactions')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_interactions')
    
    # Interactions
    is_watched = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)
    is_interested = models.BooleanField(default=False)  # For upcoming movies
    
    # Rating (4-tier system)
    RATING_CHOICES = [
        ('trash', 'Trash'),
        ('timepass', 'Timepass'),
        ('worth', 'Worth the Clock'),
        ('peak', 'Peak'),
    ]
    rating = models.CharField(max_length=20, choices=RATING_CHOICES, null=True, blank=True)
    
    # Timestamps
    watched_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_movie_interactions'
        unique_together = ('user', 'movie')
        indexes = [
            models.Index(fields=['user', 'is_watched']),
            models.Index(fields=['user', 'rating']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.movie}"


class Watchlist(models.Model):
    """User Watchlists"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    is_default = models.BooleanField(default=False)
    
    # Privacy
    PRIVACY_CHOICES = [
        ('everyone', 'Everyone'),
        ('followers', 'Followers Only'),
        ('friends', 'Friends Only'),
        ('private', 'Private'),
    ]
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='friends')
    
    # Collaboration
    is_collaborative = models.BooleanField(default=False)
    collaborators = models.ManyToManyField(User, related_name='collaborative_watchlists', blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'watchlists'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user}'s {self.name}"


class WatchlistMovie(models.Model):
    """Movies in Watchlists"""
    
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name='movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    notes = models.TextField(max_length=200, blank=True)
    added_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'watchlist_movies'
        unique_together = ('watchlist', 'movie')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.movie} in {self.watchlist}"