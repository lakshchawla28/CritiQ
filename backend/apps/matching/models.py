"""
Movie Matching System Models (real-time friendly)
"""
from django.db import models
from django.utils import timezone
from apps.authentication.models import User
from apps.movies.models import Movie
import uuid


class MatchingSession(models.Model):
    """Movie Matching Session (supports single or multi-user real-time swiping)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_matching_sessions')
    name = models.CharField(max_length=140, blank=True)
    participants = models.ManyToManyField(User, related_name='matching_sessions', blank=True)

    # Filters (applied to movie selection)
    selected_genres = models.JSONField(default=list, blank=True)  # list of genre ids or names
    theme = models.CharField(max_length=100, blank=True)
    release_year_min = models.IntegerField(null=True, blank=True)
    release_year_max = models.IntegerField(null=True, blank=True)
    max_runtime = models.IntegerField(null=True, blank=True)

    # Session state
    STATUS_CHOICES = [
        ('waiting', 'Waiting for participants'),
        ('active', 'Active (swiping)'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')

    # If a match was chosen as final
    matched_movie = models.ForeignKey(Movie, on_delete=models.SET_NULL, null=True, blank=True, related_name='matched_in_sessions')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'matching_sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"MatchingSession({self.id}) - {self.name or 'untitled'}"

    def start(self):
        """Mark session active and set timestamps."""
        self.status = 'active'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def complete(self, chosen_movie: Movie = None):
        """Complete session and optionally set chosen match."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if chosen_movie:
            self.matched_movie = chosen_movie
        self.save(update_fields=['status', 'completed_at', 'matched_movie', 'updated_at'])


class MovieSwipe(models.Model):
    """Individual swipe (like/dislike) by a participant on a movie within a session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(MatchingSession, on_delete=models.CASCADE, related_name='swipes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_swipes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='swipes')
    liked = models.BooleanField(default=False)  # True == right swipe / like
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'movie_swipes'
        unique_together = ('session', 'user', 'movie')
        indexes = [
            models.Index(fields=['session', 'movie']),
            models.Index(fields=['user', 'session']),
        ]

    def __str__(self):
        return f"{self.user} {'liked' if self.liked else 'passed'} {self.movie}"


class MatchResult(models.Model):
    """Computed match result (aggregate) for a session & movie."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(MatchingSession, on_delete=models.CASCADE, related_name='match_results')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='match_results')
    # number of users who liked it
    likes_count = models.IntegerField(default=0)
    # percent of participants who liked it (0-100)
    match_percentage = models.FloatField(default=0.0)
    matched_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'match_results'
        unique_together = ('session', 'movie')
        ordering = ['-match_percentage', '-matched_at']

    def __str__(self):
        return f"{self.movie} in {self.session} -> {self.match_percentage:.1f}%"

