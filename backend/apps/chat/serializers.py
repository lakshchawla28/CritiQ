from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import ChatRoom, Message, TypingStatus
from apps.authentication.models import User


class ChatUserMiniSerializer(serializers.ModelSerializer):
    """Minimal user object used inside chat responses"""

    class Meta:
        model = User
        fields = ["id", "username", "profile_picture"]


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""

    sender = ChatUserMiniSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "chat_room",
            "sender",
            "message_text",
            "message_type",
            "shared_content_id",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "sender",
            "read_at",
            "created_at",
            "is_read",
        ]


class TypingStatusSerializer(serializers.ModelSerializer):
    user = ChatUserMiniSerializer(read_only=True)

    class Meta:
        model = TypingStatus
        fields = ["user", "is_typing", "last_updated"]


class ChatRoomSerializer(serializers.ModelSerializer):
    """List chat rooms with last message preview"""

    participant_1 = ChatUserMiniSerializer(read_only=True)
    participant_2 = ChatUserMiniSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "participant_1",
            "participant_2",
            "last_message_text",
            "last_message_at",
            "last_message",
            "last_message_sender",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(MessageSerializer)
    def get_last_message(self, obj) -> dict | None:
        last = obj.messages.order_by("-created_at").first()
        return MessageSerializer(last, context=self.context).data if last else None


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    """Full chat room with all messages"""

    participant_1 = ChatUserMiniSerializer(read_only=True)
    participant_2 = ChatUserMiniSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "participant_1",
            "participant_2",
            "created_at",
            "updated_at",
            "messages",
        ]

class CreateChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for creating chat rooms"""

    class Meta:
        model = ChatRoom
        fields = ["participant_1", "participant_2"]

        