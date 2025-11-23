from django.contrib import admin
from .models import RecommendationPreference, Recommendation, SimilarityScore


@admin.register(RecommendationPreference)
class RecommendationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'prefer_recent_movies', 'prefer_classic_movies', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Genre Preferences', {'fields': ('favorite_genres', 'disliked_genres')}),
        ('Runtime Preferences', {'fields': ('preferred_runtime_min', 'preferred_runtime_max')}),
        ('Era Preferences', {'fields': ('prefer_recent_movies', 'prefer_classic_movies')}),
        ('Timestamps', {'fields': ('updated_at',)}),
    )


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'score', 'reason', 'is_viewed', 'is_dismissed', 'created_at']
    list_filter = ['is_viewed', 'is_dismissed', 'created_at']
    search_fields = ['user__username', 'movie__title']
    readonly_fields = ['created_at']
    ordering = ['-score', '-created_at']


@admin.register(SimilarityScore)
class SimilarityScoreAdmin(admin.ModelAdmin):
    list_display = ['user_1', 'user_2', 'similarity_score', 'calculated_at']
    search_fields = ['user_1__username', 'user_2__username']
    readonly_fields = ['calculated_at']
    ordering = ['-similarity_score']
