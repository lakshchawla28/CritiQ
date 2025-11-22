from django.contrib import admin
from .models import UserStats, UserActivity, UserPreference, BlockedUser, ReportedUser

@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_watch_streak', 'longest_watch_streak', 'total_likes_received', 'updated_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['updated_at']
    readonly_fields = ['updated_at']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username']
    ordering = ['-created_at']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications', 'push_notifications', 'theme_mode', 'updated_at']
    search_fields = ['user__username']
    list_filter = ['theme_mode', 'email_notifications']


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'blocked_user', 'blocked_at']
    search_fields = ['user__username', 'blocked_user__username']
    ordering = ['-blocked_at']


@admin.register(ReportedUser)
class ReportedUserAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reported_user', 'reason', 'status', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['reporter__username', 'reported_user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Report Info', {
            'fields': ('reporter', 'reported_user', 'reason', 'description', 'created_at')
        }),
        ('Moderation', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')
        }),
    )