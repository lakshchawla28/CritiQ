from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import UserMovieInteraction, Movie


# ----------------------------------------------------
# 1️⃣ Recalculate movie stats when a user interacts
# ----------------------------------------------------
@receiver(post_save, sender=UserMovieInteraction)
def update_movie_stats_on_save(sender, instance, created, **kwargs):
    """Recalculate watch count, interested count, and app rating when user interacts."""

    movie = instance.movie

    # --- Update watch count ---
    movie.watch_count = UserMovieInteraction.objects.filter(
        movie=movie, is_watched=True
    ).count()

    # --- Update interested count ---
    movie.interested_count = UserMovieInteraction.objects.filter(
        movie=movie, is_interested=True
    ).count()

    # --- Update average app rating ---
    rating_map = {
        "trash": 1,
        "timepass": 2,
        "worth": 3,
        "peak": 4,
    }

    ratings = UserMovieInteraction.objects.filter(movie=movie, rating__isnull=False)

    if ratings.exists():
        numeric_ratings = [rating_map.get(r.rating, None) for r in ratings]
        numeric_ratings = [r for r in numeric_ratings if r is not None]

        if numeric_ratings:
            movie.app_rating_average = sum(numeric_ratings) / len(numeric_ratings)
            movie.app_rating_count = len(numeric_ratings)
        else:
            movie.app_rating_average = 0
            movie.app_rating_count = 0
    else:
        movie.app_rating_average = 0
        movie.app_rating_count = 0

    movie.save()


# ----------------------------------------------------
# 2️⃣ Update stats if a UserMovieInteraction is deleted
# ----------------------------------------------------
@receiver(post_delete, sender=UserMovieInteraction)
def update_movie_stats_on_delete(sender, instance, **kwargs):
    """Recalculate stats if a user interaction is removed."""

    movie = instance.movie

    movie.watch_count = UserMovieInteraction.objects.filter(
        movie=movie, is_watched=True
    ).count()

    movie.interested_count = UserMovieInteraction.objects.filter(
        movie=movie, is_interested=True
    ).count()

    ratings = UserMovieInteraction.objects.filter(movie=movie)

    rating_map = {
        "trash": 1,
        "timepass": 2,
        "worth": 3,
        "peak": 4,
    }

    numeric_ratings = [
        rating_map.get(r.rating, None)
        for r in ratings if r.rating is not None
    ]

    if numeric_ratings:
        movie.app_rating_average = sum(numeric_ratings) / len(numeric_ratings)
        movie.app_rating_count = len(numeric_ratings)
    else:
        movie.app_rating_average = 0
        movie.app_rating_count = 0

    movie.save()
