from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Movie, UserMovieInteraction, Watchlist, WatchlistMovie
from apps.authentication.models import User


# ----------------------------------------
# Serializers
# ----------------------------------------

from rest_framework import serializers


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class UserMovieInteractionSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = UserMovieInteraction
        fields = "__all__"


class WatchlistMovieSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = WatchlistMovie
        fields = "__all__"


class WatchlistSerializer(serializers.ModelSerializer):
    movies = WatchlistMovieSerializer(many=True, read_only=True)

    class Meta:
        model = Watchlist
        fields = "__all__"


# ============================================================
#                      MOVIE VIEWS
# ============================================================

# 🔍 Search Movies
class SearchMoviesView(generics.ListAPIView):
    serializer_class = MovieSerializer
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
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    queryset = Movie.objects.all()


# 🔥 Popular Movies
class PopularMoviesView(generics.ListAPIView):
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Movie.objects.order_by("-tmdb_vote_average", "-tmdb_vote_count")[:50]


# ⏳ Upcoming Movies
class UpcomingMoviesView(generics.ListAPIView):
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Movie.objects.filter(is_upcoming=True).order_by("release_date")


# ============================================================
#                 USER MOVIE INTERACTIONS
# ============================================================

# 🎞 Mark Movie as Watched
class MarkMovieWatchedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

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

        return Response({"message": "Movie marked as watched"}, status=200)


# ⭐ Rate Movie
class RateMovieView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        rating = request.data.get("rating")

        if rating not in ["trash", "timepass", "worth", "peak"]:
            return Response({"error": "Invalid rating."}, status=400)

        movie = get_object_or_404(Movie, id=movie_id)

        interaction, _ = UserMovieInteraction.objects.get_or_create(
            user=request.user,
            movie=movie
        )

        interaction.rating = rating
        interaction.save()

        movie.app_rating_count = movie.user_interactions.exclude(rating=None).count()
        movie.save(update_fields=["app_rating_count"])

        return Response({"message": "Rating submitted"}, status=200)


# 👀 Mark Interested
class MarkInterestedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

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

        return Response({"message": "Marked as interested"}, status=200)


# ============================================================
#                          WATCHLISTS
# ============================================================

# 📄 List User Watchlists
class UserWatchlistView(generics.ListAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)


# ➕ Create Watchlist
class CreateWatchlistView(generics.CreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
