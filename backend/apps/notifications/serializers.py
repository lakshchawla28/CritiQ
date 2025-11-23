from rest_framework import serializers
from .models import Notification, PushToken
from apps.authentication.models import User


class RelatedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']


class NotificationSerializer(serializers.ModelSerializer):
    related_user = RelatedUserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'related_user', 'related_object_id', 'related_object_type',
            'action_url', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = ['id', 'device_type', 'token', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']