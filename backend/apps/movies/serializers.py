from rest_framework import serializers
from .models import Movie, UserMovieInteraction, Watchlist, WatchlistMovie


# ======================================================
#   MOVIE SERIALIZER
# ======================================================

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "tmdb_id",
            "title",
            "original_title",
            "overview",
            "poster_path",
            "backdrop_path",
            "release_date",
            "runtime",
            "genres",
            "original_language",
            "tmdb_vote_average",
            "tmdb_vote_count",
            "app_rating_average",
            "app_rating_count",
            "watch_count",
            "interested_count",
            "is_upcoming",
            "created_at",
            "updated_at",
            "last_synced",
        ]


# ======================================================
#   USER ⟷ MOVIE INTERACTION SERIALIZER
# ======================================================

class UserMovieInteractionSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = UserMovieInteraction
        fields = [
            "user",
            "movie",
            "is_watched",
            "is_liked",
            "is_interested",
            "rating",
            "watched_date",
            "created_at",
            "updated_at",
        ]


# ======================================================
#   WATCHLIST MOVIE SERIALIZER
# ======================================================

class WatchlistMovieSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = WatchlistMovie
        fields = [
            "id",
            "movie",
            "added_by",
            "notes",
            "added_at",
        ]


# ======================================================
#   WATCHLIST SERIALIZER
# ======================================================

class WatchlistSerializer(serializers.ModelSerializer):
    movies = WatchlistMovieSerializer(many=True, read_only=True)

    class Meta:
        model = Watchlist
        fields = [
            "id",
            "user",
            "name",
            "description",
            "is_default",
            "privacy",
            "is_collaborative",
            "collaborators",
            "created_at",
            "updated_at",
            "movies",
        ]
