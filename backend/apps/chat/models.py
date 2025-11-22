"""
Chat System Models
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
import uuid

class ChatRoom(models.Model):
    """Chat Room (One-on-One)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Participants (always 2 for one-on-one)
    participant_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms_as_p1')
    participant_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms_as_p2')
    
    # Last message info (for sorting)
    last_message_text = models.TextField(max_length=100, blank=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message_sender = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-last_message_at']
        unique_together = ('participant_1', 'participant_2')
    
    def __str__(self):
        return f"Chat: {self.participant_1} & {self.participant_2}"


class Message(models.Model):
    """Chat Message"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_text = models.TextField(max_length=5000)
    
    # Message type
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('movie_share', 'Movie Share'),
        ('review_share', 'Review Share'),
    ]
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    
    # Shared content (for movie/review shares)
    shared_content_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Read status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat_room', 'created_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender} in {self.chat_room.id}"


class TypingStatus(models.Model):
    """Track typing indicators"""
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='typing_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'typing_statuses'
        unique_together = ('chat_room', 'user')
    
    def __str__(self):
        return f"{self.user} typing in {self.chat_room.id}"