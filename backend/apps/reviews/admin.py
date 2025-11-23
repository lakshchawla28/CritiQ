from django.contrib import admin
from .models import Review, ReviewLike, ReviewComment, ReviewRepost, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'usage_count', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['usage_count', 'created_at']
    ordering = ['name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'contains_spoilers', 'privacy', 'created_at']
    list_filter = ['rating', 'contains_spoilers', 'privacy', 'created_at']
    search_fields = ['user__username', 'movie__title', 'review_text']
    readonly_fields = ['created_at', 'updated_at', 'likes_count', 'comments_count', 'reposts_count']
    
    fieldsets = (
        ('Review Info', {'fields': ('user', 'movie', 'rating', 'review_text', 'tags')}),
        ('Settings', {'fields': ('contains_spoilers', 'privacy')}),
        ('Stats', {'fields': ('likes_count', 'comments_count', 'reposts_count')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'review', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'review', 'comment_text', 'created_at']
    search_fields = ['user__username', 'comment_text']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ReviewRepost)
class ReviewRepostAdmin(admin.ModelAdmin):
    list_display = ['user', 'original_review', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
