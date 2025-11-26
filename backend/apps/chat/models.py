"""
Chat System Models (PostgreSQL Optimized)
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
import uuid


class ChatRoom(models.Model):
    """
    One-to-one chat room between 2 users.
    We enforce ordering so (A,B) and (B,A) cannot be created twice.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    participant_1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chatrooms_as_p1"
    )
    participant_2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chatrooms_as_p2"
    )

    last_message_text = models.TextField(max_length=100, blank=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message_sender = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_rooms"
        ordering = ["-last_message_at"]
        unique_together = ("participant_1", "participant_2")

    def save(self, *args, **kwargs):
        if self.participant_1 and self.participant_2:
            if str(self.participant_1.id) > str(self.participant_2.id):
                self.participant_1, self.participant_2 = (
                    self.participant_2,
                    self.participant_1,
                )
        super().save(*args, **kwargs)

    def get_other_participant(self, user):
        if user == self.participant_1:
            return self.participant_2
        if user == self.participant_2:
            return self.participant_1
        return None

    def __str__(self):
        return f"Chat: {self.participant_1.username} & {self.participant_2.username}"


class Message(models.Model):
    """Chat message"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )

    message_text = models.TextField(max_length=5000)

    MESSAGE_TYPE_CHOICES = [
        ("text", "Text"),
        ("movie_share", "Movie Share"),
        ("review_share", "Review Share"),
    ]
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPE_CHOICES, default="text"
    )

    shared_content_id = models.TextField(blank=True, null=True)

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["chat_room", "created_at"])]

    def __str__(self):
        return f"Message from {self.sender.username} in {self.chat_room.id}"


class TypingStatus(models.Model):
    """Typing indicator"""

    chat_room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="typing_statuses"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    is_typing = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "typing_statuses"
        unique_together = ("chat_room", "user")

    def __str__(self):
        return f"{self.user.username} typing in {self.chat_room.id}"

