"""
Movie Matching System Models
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
from apps.movies.models import Movie
import uuid

class MatchingSession(models.Model):
    """Movie Matching Session"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    
    # Session name
    name = models.CharField(max_length=100, blank=True)
    
    # Participants
    participants = models.ManyToManyField(User, related_name='matching_sessions')
    
    # Filters
    selected_genres = models.JSONField(default=list)  # List of genre IDs
    theme = models.CharField(max_length=100, blank=True)  # e.g., "Date Night", "Family Movie"
    release_year_min = models.IntegerField(null=True, blank=True)
    release_year_max = models.IntegerField(null=True, blank=True)
    max_runtime = models.IntegerField(null=True, blank=True)
    
    # Session status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Match found
    matched_movie = models.ForeignKey(Movie, null=True, blank=True, on_delete=models.SET_NULL, related_name='matched_in_sessions')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'matching_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Matching Session: {self.name or self.id}"


class MovieSwipe(models.Model):
    """Individual swipes in a matching session"""
    
    session = models.ForeignKey(MatchingSession, on_delete=models.CASCADE, related_name='swipes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_swipes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    
    # Swipe direction
    SWIPE_CHOICES = [
        ('right', 'Right (Like)'),
        ('left', 'Left (Pass)'),
    ]
    swipe_direction = models.CharField(max_length=10, choices=SWIPE_CHOICES)
    
    swiped_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'movie_swipes'
        unique_together = ('session', 'user', 'movie')
        indexes = [
            models.Index(fields=['session', 'movie']),
        ]
    
    def __str__(self):
        return f"{self.user} swiped {self.swipe_direction} on {self.movie}"


class MatchResult(models.Model):
    """Matched movies in a session"""
    
    session = models.ForeignKey(MatchingSession, on_delete=models.CASCADE, related_name='match_results')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    
    # Users who swiped right
    matched_users = models.ManyToManyField(User, related_name='matched_movies')
    match_percentage = models.FloatField()  # Percentage of participants who liked it
    
    matched_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'match_results'
        unique_together = ('session', 'movie')
        ordering = ['-match_percentage', '-matched_at']
    
    def __str__(self):
        return f"Match: {self.movie} ({self.match_percentage}%)"