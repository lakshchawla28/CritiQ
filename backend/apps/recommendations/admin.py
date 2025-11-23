from django.contrib import admin
from .models import Recommendation, UserPreference


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "movie",
        "score",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("user__username", "movie__title")
    ordering = ("-score", "-created_at")


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "favorite_genres_display",
        "disliked_genres_display",
        "updated_at",
    )
    search_fields = ("user__username",)
    ordering = ("-updated_at",)
    readonly_fields = ("updated_at",)

    # Display readable genres
    def favorite_genres_display(self, obj):
        genres = obj.favorite_genres or []
        return ", ".join(genres) if isinstance(genres, list) else str(genres)
    favorite_genres_display.short_description = "favorite_genres"

    def disliked_genres_display(self, obj):
        genres = obj.disliked_genres or []
        return ", ".join(genres) if isinstance(genres, list) else str(genres)
    disliked_genres_display.short_description = "disliked_genres"
