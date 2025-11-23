"""
Notifications System Models
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
import uuid


class Notification(models.Model):
    """User Notifications"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    NOTIFICATION_TYPES = [
        ('follow_request', 'Follow Request'),
        ('follow_accepted', 'Follow Request Accepted'),
        ('chat_request', 'Chat Request'),
        ('chat_accepted', 'Chat Request Accepted'),
        ('review_liked', 'Review Liked'),
        ('review_commented', 'Review Commented'),
        ('review_reposted', 'Review Reposted'),
        ('achievement_earned', 'Achievement Earned'),
        ('match_found', 'Match Found'),
        ('mentioned', 'Mentioned'),
        ('new_follower', 'New Follower'),
    ]
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    
    title = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    
    # Related objects
    related_user = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='notifications_about'
    )
    related_object_id = models.CharField(max_length=100, null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)  # 'review', 'post', 'achievement', etc.
    
    # URL to navigate to
    action_url = models.CharField(max_length=200, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class PushToken(models.Model):
    """Store user's push notification tokens"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_tokens')
    
    DEVICE_TYPES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    
    token = models.CharField(max_length=500, unique=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'push_tokens'
        unique_together = ('user', 'token')
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type}"