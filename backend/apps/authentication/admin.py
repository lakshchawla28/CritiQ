from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification, FollowRequest, UserFollow, ChatRequest

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'full_name', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'is_staff', 'created_at']
    search_fields = ['email', 'username', 'phone_number', 'full_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'full_name', 'bio', 'profile_picture', 'date_of_birth')}),
        ('Contact', {'fields': ('phone_number',)}),
        ('OTT Platforms', {'fields': ('netflix_profile', 'prime_video_profile', 'disney_plus_profile', 'hbo_max_profile')}),
        ('Privacy', {'fields': ('reviews_privacy', 'ratings_privacy', 'watchlist_privacy', 'watch_history_privacy')}),
        ('Stats', {'fields': ('total_watch_time_minutes', 'movies_watched_count', 'reviews_count', 'followers_count', 'following_count')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'email_verified', 'phone_verified')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    readonly_fields = ['created_at', 'total_watch_time_minutes', 'movies_watched_count', 'reviews_count', 'followers_count', 'following_count']

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'otp_code', 'verification_type', 'is_verified', 'created_at']
    list_filter = ['verification_type', 'is_verified', 'created_at']
    search_fields = ['phone_number', 'email', 'otp_code']


@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__email', 'to_user__email']


@admin.register(ChatRequest)
class ChatRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__email', 'to_user__email']
