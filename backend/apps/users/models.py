from django.db import models
from django.utils import timezone
from apps.authentication.models import User
import uuid

class UserStats(models.Model):
    """Extended user statistics and analytics"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extended_stats')
    
    # Viewing patterns
    most_watched_genre = models.JSONField(default=dict)  # {genre_id: count}
    favorite_decade = models.CharField(max_length=10, blank=True)  # e.g., "1990s"
    average_movie_length = models.IntegerField(default=0)  # in minutes
    
    # Activity stats
    most_active_day = models.CharField(max_length=10, blank=True)  # e.g., "Saturday"
    most_active_hour = models.IntegerField(null=True, blank=True)  # 0-23
    
    # Social stats
    most_liked_review = models.ForeignKey(
        'reviews.Review',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    total_likes_received = models.IntegerField(default=0)
    total_comments_made = models.IntegerField(default=0)
    
    # Streaks
    current_watch_streak = models.IntegerField(default=0)  # days
    longest_watch_streak = models.IntegerField(default=0)  # days
    last_watch_date = models.DateField(null=True, blank=True)
    
    # Rankings (percentile among all users)
    movies_watched_percentile = models.FloatField(default=0)
    reviews_written_percentile = models.FloatField(default=0)
    
    # Last updated
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_stats'
    
    def __str__(self):
        return f"Stats for {self.user.username}"


class UserActivity(models.Model):
    """Track user activity for analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    ACTIVITY_TYPES = [
        ('movie_watched', 'Movie Watched'),
        ('review_posted', 'Review Posted'),
        ('review_liked', 'Review Liked'),
        ('comment_posted', 'Comment Posted'),
        ('user_followed', 'User Followed'),
        ('movie_rated', 'Movie Rated'),
        ('watchlist_created', 'Watchlist Created'),
        ('achievement_earned', 'Achievement Earned'),
        ('session_created', 'Matching Session Created'),
    ]
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    
    # Related objects (store as JSON for flexibility)
    related_data = models.JSONField(default=dict)
    
    # Timestamp
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'user_activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_setting_preferences')

    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    notify_on_follow = models.BooleanField(default=True)
    notify_on_comment = models.BooleanField(default=True)
    notify_on_like = models.BooleanField(default=True)
    notify_on_mention = models.BooleanField(default=True)
    notify_on_new_follower = models.BooleanField(default=True)
    notify_on_chat_request = models.BooleanField(default=True)
    notify_on_match_found = models.BooleanField(default=True)

    show_spoilers = models.BooleanField(default=False)
    mature_content = models.BooleanField(default=False)

    preferred_language = models.CharField(max_length=10, default='en')
    preferred_region = models.CharField(max_length=10, default='US')

    autoplay_trailers = models.BooleanField(default=True)
    theme_mode = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto'
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_settings_preferences"

    def __str__(self):
        return f"UI Preferences for {self.user.username}"


class BlockedUser(models.Model):
    """Users that have been blocked"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    
    reason = models.TextField(max_length=500, blank=True)
    blocked_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'blocked_users'
        unique_together = ('user', 'blocked_user')
        ordering = ['-blocked_at']
    
    def __str__(self):
        return f"{self.user.username} blocked {self.blocked_user.username}"


class ReportedUser(models.Model):
    """User reports for moderation"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake_account', 'Fake Account'),
        ('impersonation', 'Impersonation'),
        ('other', 'Other'),
    ]
    
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(max_length=1000)
    
    # Moderation status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reports_reviewed'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'reported_users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report: {self.reported_user.username} by {self.reporter.username}"


class ReportedContent(models.Model):
    """Report reviews, posts, or comments"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_reports_made')
    
    CONTENT_TYPES = [
        ('review', 'Review'),
        ('post', 'Post'),
        ('comment', 'Comment'),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.CharField(max_length=100)  # UUID of the review/post/comment
    
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('misinformation', 'Misinformation'),
        ('spoilers', 'Unmarked Spoilers'),
        ('copyright', 'Copyright Violation'),
        ('other', 'Other'),
    ]
    
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(max_length=1000)
    
    # Moderation status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='content_reports_reviewed'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'reported_content'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Report: {self.content_type} by {self.reporter.username}"