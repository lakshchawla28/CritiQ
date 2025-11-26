from rest_framework import serializers
from .models import MatchingSession, MovieSwipe, MatchResult
from apps.authentication.models import User
from apps.movies.serializers import MovieSerializer  # using your movies app serializer


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']


class MatchingSessionCreateSerializer(serializers.ModelSerializer):
    """Used to create sessions; participants may be added after creation."""
    selected_genres = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = MatchingSession
        fields = ['id', 'name', 'selected_genres', 'theme', 'release_year_min', 'release_year_max', 'max_runtime']

    def create(self, validated_data):
        # created_by is injected in view (serializer.save(created_by=request.user))
        return super().create(validated_data)


class MatchingSessionSerializer(serializers.ModelSerializer):
    created_by = UserMiniSerializer(read_only=True)
    participants = UserMiniSerializer(read_only=True, many=True)

    class Meta:
        model = MatchingSession
        fields = ['id', 'name', 'created_by', 'participants', 'status', 'selected_genres', 'theme', 'release_year_min', 'release_year_max', 'max_runtime', 'created_at', 'started_at', 'updated_at']


class MovieSwipeSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    # Accept movie id for creation/update
    movie_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = MovieSwipe
        fields = ['id', 'session', 'user', 'movie', 'movie_id', 'liked', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'movie', 'created_at', 'updated_at', 'session']

    def create(self, validated_data):
        # normally view resolves movie and calls save() — keep here for safety
        movie_id = validated_data.pop('movie_id', None)
        if movie_id and 'movie' not in validated_data:
            from apps.movies.models import Movie
            validated_data['movie'] = Movie.objects.get(id=movie_id)
        return super().create(validated_data)


class MatchResultSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = MatchResult
        fields = ['id', 'movie', 'likes_count', 'match_percentage', 'matched_at']


