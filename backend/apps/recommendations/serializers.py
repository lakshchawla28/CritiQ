from rest_framework import serializers
from apps.recommendations.models import (
    Recommendation,
    UserPreference,
    SimilarityScore
)
from apps.movies.models import Movie
from apps.movies.serializers import MovieSerializer  # If you already have it


# ======================================================
#   USER PREFERENCE SERIALIZER
# ======================================================

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            "favorite_genres",
            "disliked_genres",
            "preferred_runtime_min",
            "preferred_runtime_max",
            "prefer_recent_movies",
            "prefer_classic_movies",
            "updated_at"
        ]


# ======================================================
#   RECOMMENDATION SERIALIZER
# ======================================================

class RecommendationSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            "id",
            "user",
            "movie",
            "score",
            "reason",
            "is_viewed",
            "is_dismissed",
            "created_at",
        ]


# ======================================================
#   SIMILARITY SCORE SERIALIZER (Optional)
# ======================================================

class SimilarityScoreSerializer(serializers.ModelSerializer):
    user_1 = serializers.CharField(source="user_1.username")
    user_2 = serializers.CharField(source="user_2.username")

    class Meta:
        model = SimilarityScore
        fields = [
            "user_1",
            "user_2",
            "similarity_score",
            "calculated_at",
        ]
