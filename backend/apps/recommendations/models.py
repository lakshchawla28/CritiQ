"""
Recommendation System Models
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
from apps.movies.models import Movie
import uuid


class UserPreference(models.Model):
    """
    Additional user viewing preferences that improve recommendations.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="recommendation_preferences"
    )

    # Genre preferences
    favorite_genres = models.JSONField(default=dict)  # {genre_id: weight}
    disliked_genres = models.JSONField(default=list)  # [genre_id, ...]

    # Runtime preference
    preferred_runtime_min = models.IntegerField(default=80)
    preferred_runtime_max = models.IntegerField(default=180)

    # Release-year preferences
    prefer_recent_movies = models.BooleanField(default=True)
    prefer_classic_movies = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recommendation_user_preferences"

    def __str__(self):
        return f"Recommendation Preferences for {self.user}"


class Recommendation(models.Model):
    """
    Final recommended movies stored for each user.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recommendations"
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="recommended_to"
    )

    # Score normalized between 0 and 1
    score = models.FloatField()

    reason = models.CharField(max_length=50, blank=True)

    is_viewed = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "recommendations"
        unique_together = ("user", "movie")
        ordering = ["-score", "-created_at"]
        indexes = [
            models.Index(fields=["user", "-score"]),
        ]

    def __str__(self):
        return f"Recommend {self.movie} to {self.user}"


class SimilarityScore(models.Model):
    """
    User–User similarity used for collaborative filtering.
    """

    user_1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="similarity_as_user1"
    )

    user_2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="similarity_as_user2"
    )

    similarity_score = models.FloatField()  # cosine similarity 0–1
    calculated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "similarity_scores"
        unique_together = ("user_1", "user_2")
        indexes = [
            models.Index(fields=["user_1", "-similarity_score"]),
        ]

    def __str__(self):
        return f"Similarity: {self.user_1} & {self.user_2} = {self.similarity_score}"
