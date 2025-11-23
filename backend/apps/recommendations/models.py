"""
Recommendation System Models
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
from apps.movies.models import Movie
import uuid

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recommendation_preferences')

    favorite_genres = models.JSONField(default=dict)
    disliked_genres = models.JSONField(default=list)

    preferred_runtime_min = models.IntegerField(default=80)
    preferred_runtime_max = models.IntegerField(default=180)

    prefer_recent_movies = models.BooleanField(default=True)
    prefer_classic_movies = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recommendation_user_preferences"

    def __str__(self):
        return f"Recommendation Preferences for {self.user}"



class Recommendation(models.Model):
    """Generated recommendations for users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    
    # Recommendation score (0-1)
    score = models.FloatField()
    
    # Recommendation reason
    REASON_CHOICES = [
        ('genre_match', 'Based on your favorite genres'),
        ('similar_users', 'Users like you enjoyed this'),
        ('trending', 'Trending now'),
        ('high_rated', 'Highly rated'),
        ('new_release', 'New release you might like'),
    ]
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    
    # Status
    is_viewed = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'recommendations'
        unique_together = ('user', 'movie')
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-score']),
        ]
    
    def __str__(self):
        return f"Recommend {self.movie} to {self.user}"


class SimilarityScore(models.Model):
    """Pre-computed similarity scores between users"""
    
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='similarity_as_user1')
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='similarity_as_user2')
    
    # Cosine similarity score (0-1)
    similarity_score = models.FloatField()
    
    # Last calculated
    calculated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'similarity_scores'
        unique_together = ('user_1', 'user_2')
        indexes = [
            models.Index(fields=['user_1', '-similarity_score']),
        ]
    
    def __str__(self):
        return f"Similarity: {self.user_1} & {self.user_2} = {self.similarity_score}"