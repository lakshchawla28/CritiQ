from django.contrib import admin
from .models import MatchingSession, MovieSwipe, MatchResult

@admin.register(MatchingSession)
class MatchingSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'status', 'created_at', 'started_at', 'completed_at')
    list_filter = ('status', 'theme', 'created_at')
    search_fields = ('name', 'created_by__email', 'created_by__username')


@admin.register(MovieSwipe)
class MovieSwipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user', 'movie', 'liked', 'created_at')
    search_fields = ('user__email', 'user__username', 'movie__title')


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('session', 'movie', 'likes_count', 'match_percentage', 'matched_at')
    ordering = ('-match_percentage',)
