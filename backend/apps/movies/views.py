# apps/movies/views.py
from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Movie, UserMovieInteraction, Watchlist, WatchlistMovie
from apps.authentication.models import User

# Import canonical serializers from the app's serializers.py to avoid duplicate component names
from .serializers import (
    MovieSerializer as CanonicalMovieSerializer,
    UserMovieInteractionSerializer as CanonicalUserMovieInteractionSerializer,
    WatchlistSerializer as CanonicalWatchlistSerializer,
    WatchlistMovieSerializer as CanonicalWatchlistMovieSerializer,
)

# ---------------------------
# Lightweight input serializers
# ---------------------------
class EmptySerializer(serializers.Serializer):
    """Used for endpoints that do not accept body (present to satisfy spectacular)."""
    pass


class RatingSerializer(serializers.Serializer):
    rating = serializers.ChoiceField(choices=["trash", "timepass", "worth", "peak"])


# ============================================================
#                      MOVIE VIEWS
# ============================================================

# 🔍 Search Movies
class SearchMoviesView(generics.ListAPIView):
    serializer_class = CanonicalMovieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        return Movie.objects.filter(
            Q(title__icontains=query) |
            Q(original_title__icontains=query) |
            Q(overview__icontains=query)
        ).order_by("-release_date")


# 🎬 Movie Details
class MovieDetailView(generics.RetrieveAPIView):
    serializer_class = CanonicalMovieSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    queryset = Movie.objects.all()


# 🔥 Popular Movies
class PopularMoviesView(generics.ListAPIView):
    serializer_class = CanonicalMovieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Movie.objects.order_by("-tmdb_vote_average", "-tmdb_vote_count")[:50]


# ⏳ Upcoming Movies
class UpcomingMoviesView(generics.ListAPIView):
    serializer_class = CanonicalMovieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Movie.objects.filter(is_upcoming=True).order_by("release_date")


# ============================================================
#                 USER MOVIE INTERACTIONS
# ============================================================

# 🎞 Mark Movie as Watched
class MarkMovieWatchedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer  # endpoint doesn't require a body, but serializer helps schema generation

    def post(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)

        interaction, _ = UserMovieInteraction.objects.get_or_create(
            user=request.user,
            movie=movie
        )

        interaction.is_watched = True
        interaction.watched_date = timezone.now()
        interaction.save()

        movie.watch_count = movie.user_interactions.filter(is_watched=True).count()
        movie.save(update_fields=["watch_count"])

        return Response({"message": "Movie marked as watched"}, status=status.HTTP_200_OK)


# ⭐ Rate Movie
class RateMovieView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RatingSerializer  # describes request body for rating endpoint

    def post(self, request, movie_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.validated_data["rating"]

        movie = get_object_or_404(Movie, id=movie_id)

        interaction, _ = UserMovieInteraction.objects.get_or_create(
            user=request.user,
            movie=movie
        )

        interaction.rating = rating
        interaction.save()

        movie.app_rating_count = movie.user_interactions.exclude(rating=None).count()
        movie.save(update_fields=["app_rating_count"])

        return Response({"message": "Rating submitted"}, status=status.HTTP_200_OK)


# 👀 Mark Interested
class MarkInterestedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer  # no body expected

    def post(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)

        interaction, _ = UserMovieInteraction.objects.get_or_create(
            user=request.user,
            movie=movie
        )

        interaction.is_interested = True
        interaction.save()

        movie.interested_count = movie.user_interactions.filter(is_interested=True).count()
        movie.save(update_fields=["interested_count"])

        return Response({"message": "Marked as interested"}, status=status.HTTP_200_OK)


# ============================================================
#                          WATCHLISTS
# ============================================================

# 📄 List User Watchlists
class UserWatchlistView(generics.ListAPIView):
    serializer_class = CanonicalWatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)


# ➕ Create Watchlist
class CreateWatchlistView(generics.CreateAPIView):
    serializer_class = CanonicalWatchlistSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddMovieToWatchlistView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CanonicalWatchlistMovieSerializer

    def post(self, request, watchlist_id, movie_id):
        watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
        movie = get_object_or_404(Movie, id=movie_id)

        watchlist_movie, created = WatchlistMovie.objects.get_or_create(
            watchlist=watchlist,
            movie=movie
        )

        if created:
            watchlist_movie.added_at = timezone.now()
            watchlist_movie.save()

        serializer = self.get_serializer(watchlist_movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

# ➖ Remove Movie from Watchlist
class RemoveMovieFromWatchlistView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer  # no body expected

    def delete(self, request, watchlist_id, movie_id):
        watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
        movie = get_object_or_404(Movie, id=movie_id)

        watchlist_movie = WatchlistMovie.objects.filter(
            watchlist=watchlist,
            movie=movie
        ).first()

        if watchlist_movie:
            watchlist_movie.delete()
            return Response({"message": "Movie removed from watchlist"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Movie not found in watchlist"}, status=status.HTTP_404_NOT_FOUND)
        

        