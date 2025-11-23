from rest_framework import serializers
from .models import ChatRoom, Message, TypingStatus
from apps.authentication.models import User


# ======================================================
# USER (MINIMAL SERIALIZER)
# ======================================================
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "profile_picture"]


# ======================================================
# MESSAGE SERIALIZER
# ======================================================
class MessageSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)

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


# ======================================================
# TYPING STATUS SERIALIZER
# ======================================================
class TypingStatusSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = TypingStatus
        fields = ["user", "is_typing", "last_updated"]


# ======================================================
# CHAT ROOM SERIALIZER
# ======================================================
class ChatRoomSerializer(serializers.ModelSerializer):
    participant_1 = UserMiniSerializer(read_only=True)
    participant_2 = UserMiniSerializer(read_only=True)
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

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        return MessageSerializer(last).data if last else None


# ======================================================
# CHAT ROOM DETAIL SERIALIZER (INCLUDES MESSAGES)
# ======================================================
class ChatRoomDetailSerializer(serializers.ModelSerializer):
    participant_1 = UserMiniSerializer(read_only=True)
    participant_2 = UserMiniSerializer(read_only=True)
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
