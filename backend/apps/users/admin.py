from django.contrib import admin
from .models import (
    UserStats, UserActivity, UserPreference, 
    BlockedUser, ReportedUser, ReportedContent
)


@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_watch_streak', 'longest_watch_streak', 'total_likes_received', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Viewing Patterns', {'fields': ('most_watched_genre', 'favorite_decade', 'average_movie_length')}),
        ('Activity', {'fields': ('most_active_day', 'most_active_hour')}),
        ('Social Stats', {'fields': ('most_liked_review', 'total_likes_received', 'total_comments_made')}),
        ('Streaks', {'fields': ('current_watch_streak', 'longest_watch_streak', 'last_watch_date')}),
        ('Rankings', {'fields': ('movies_watched_percentile', 'reviews_written_percentile')}),
        ('Timestamps', {'fields': ('updated_at',)}),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications', 'push_notifications', 'theme_mode', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Notifications', {'fields': (
            'email_notifications', 'push_notifications', 
            'notify_on_follow', 'notify_on_comment', 'notify_on_like',
            'notify_on_mention', 'notify_on_new_follower', 
            'notify_on_chat_request', 'notify_on_match_found'
        )}),
        ('Content Settings', {'fields': ('show_spoilers', 'mature_content')}),
        ('Preferences', {'fields': ('preferred_language', 'preferred_region', 'autoplay_trailers', 'theme_mode')}),
        ('Timestamps', {'fields': ('updated_at',)}),
    )


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'blocked_user', 'blocked_at']
    search_fields = ['user__username', 'blocked_user__username']
    readonly_fields = ['blocked_at']
    ordering = ['-blocked_at']


@admin.register(ReportedUser)
class ReportedUserAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reported_user', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['reporter__username', 'reported_user__username', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Report Info', {'fields': ('reporter', 'reported_user', 'reason', 'description')}),
        ('Moderation', {'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


@admin.register(ReportedContent)
class ReportedContentAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'content_type', 'content_id', 'reason', 'status', 'created_at']
    list_filter = ['content_type', 'reason', 'status', 'created_at']
    search_fields = ['reporter__username', 'content_id', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Report Info', {'fields': ('reporter', 'content_type', 'content_id', 'reason', 'description')}),
        ('Moderation', {'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )