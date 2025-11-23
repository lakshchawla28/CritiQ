from rest_framework import serializers
from apps.recommendations.models import (
    RecommendationPreference,  # ← CHANGED from UserPreference
    Recommendation,
    SimilarityScore
)
from apps.movies.models import Movie
from apps.authentication.models import User


class MovieSerializer(serializers.ModelSerializer):
    """Minimal movie serializer for recommendations"""
    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'title', 'poster_path', 'release_date', 'genres']


class RecommendationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user recommendation preferences"""
    class Meta:
        model = RecommendationPreference
        fields = [
            'favorite_genres',
            'disliked_genres',
            'preferred_runtime_min',
            'preferred_runtime_max',
            'prefer_recent_movies',
            'prefer_classic_movies',
            'updated_at'
        ]
        read_only_fields = ['updated_at']


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer for movie recommendations"""
    movie = MovieSerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id',
            'movie',
            'score',
            'reason',
            'is_viewed',
            'is_dismissed',
            'created_at'
        ]
        read_only_fields = ['id', 'score', 'reason', 'created_at']


class SimilarityScoreSerializer(serializers.ModelSerializer):
    """Serializer for user similarity scores"""
    user_1_username = serializers.CharField(source='user_1.username', read_only=True)
    user_2_username = serializers.CharField(source='user_2.username', read_only=True)
    
    class Meta:
        model = SimilarityScore
        fields = [
            'user_1',
            'user_1_username',
            'user_2',
            'user_2_username',
            'similarity_score',
            'calculated_at'
        ]
        read_only_fields = ['calculated_at']