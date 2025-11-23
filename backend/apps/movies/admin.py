from django.contrib import admin
from .models import Movie, UserMovieInteraction, Watchlist, WatchlistMovie


# ============================
# Movie Admin
# ============================
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "tmdb_id",
        "release_date",
        "runtime",
        "tmdb_vote_average",
        "app_rating_average",
        "is_upcoming",
    )
    list_filter = ("is_upcoming", "original_language", "release_date")
    search_fields = ("title", "original_title", "tmdb_id")
    ordering = ("-release_date",)
    readonly_fields = ("created_at", "updated_at", "last_synced")


# ============================
# User Movie Interaction Admin
# ============================
@admin.register(UserMovieInteraction)
class UserMovieInteractionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "movie",
        "is_watched",
        "is_liked",
        "is_interested",
        "rating",
        "watched_date",
    )
    list_filter = ("is_watched", "is_liked", "rating")
    search_fields = ("user__username", "movie__title")
    ordering = ("-updated_at",)


# ============================
# Watchlist Admin
# ============================
@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "is_default",
        "privacy",
        "is_collaborative",
        "created_at",
    )
    list_filter = ("privacy", "is_collaborative")
    search_fields = ("name", "user__username")
    ordering = ("-created_at",)
    filter_horizontal = ("collaborators",)


# ============================
# Watchlist Movie Admin
# ============================
@admin.register(WatchlistMovie)
class WatchlistMovieAdmin(admin.ModelAdmin):
    list_display = (
        "movie",
        "watchlist",
        "added_by",
        "added_at",
    )
    search_fields = ("movie__title", "watchlist__name", "added_by__username")
    ordering = ("-added_at",)
