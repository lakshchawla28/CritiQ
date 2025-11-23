from rest_framework import serializers
from .models import MatchingSession, MovieSwipe, MatchResult
from apps.movies.serializers import MovieSerializer
from apps.authentication.models import User


# ======================================================
# USER MINI SERIALIZER (used for participants)
# ======================================================

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "profile_picture"]


# ======================================================
# MOVIE SWIPE SERIALIZER
# ======================================================

class MovieSwipeSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = MovieSwipe
        fields = [
            "id",
            "user",
            "movie",
            "liked",
            "created_at",
        ]


# ======================================================
# MATCH RESULT SERIALIZER
# ======================================================

class MatchResultSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = MatchResult
        fields = [
            "id",
            "movie",
            "match_score",
            "created_at",
        ]


# ======================================================
# MATCHING SESSION SERIALIZER (LIST VIEW)
# ======================================================

class MatchingSessionSerializer(serializers.ModelSerializer):
    created_by = UserMiniSerializer(read_only=True)
    participants = UserMiniSerializer(read_only=True, many=True)

    class Meta:
        model = MatchingSession
        fields = [
            "id",
            "created_by",
            "participants",
            "is_active",
            "created_at",
        ]


# ======================================================
# MATCHING SESSION DETAIL (FULL DATA + SWIPES + MATCH RESULTS)
# ======================================================

class MatchingSessionDetailSerializer(serializers.ModelSerializer):
    created_by = UserMiniSerializer(read_only=True)
    participants = UserMiniSerializer(read_only=True, many=True)
    swipes = MovieSwipeSerializer(many=True, read_only=True)
    match_results = MatchResultSerializer(many=True, read_only=True)

    class Meta:
        model = MatchingSession
        fields = [
            "id",
            "created_by",
            "participants",
            "is_active",
            "created_at",
            "swipes",
            "match_results",
        ]
