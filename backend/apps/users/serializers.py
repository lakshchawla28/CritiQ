from rest_framework import serializers
from apps.authentication.models import User
from apps.authentication.serializers import UserProfileSerializer
from .models import UserStats, UserActivity, UserPreference, BlockedUser, ReportedUser

# ----- Utility / small request serializers used by views -----
class EmptySerializer(serializers.Serializer):
    """Used for endpoints that require a serializer for schema generation but accept no body."""
    pass


class BlockUserRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)


class ReportUserSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(choices=[r[0] for r in ReportedUser.REPORT_REASONS])
    description = serializers.CharField(max_length=1000)


# ----- Primary serializers -----
class UserStatsSerializer(serializers.ModelSerializer):
    """Serialize user statistics"""
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = UserStats
        fields = [
            'id', 'user', 'most_watched_genre', 'favorite_decade',
            'average_movie_length', 'most_active_day', 'most_active_hour',
            'total_likes_received', 'total_comments_made',
            'current_watch_streak', 'longest_watch_streak',
            'last_watch_date', 'movies_watched_percentile',
            'reviews_written_percentile', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'updated_at']


class UserActivitySerializer(serializers.ModelSerializer):
    """Serialize user activities"""
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_username', 'activity_type',
            'related_data', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serialize user preferences"""

    class Meta:
        model = UserPreference
        fields = [
            'id', 'user', 'email_notifications', 'push_notifications',
            'notify_on_follow', 'notify_on_comment', 'notify_on_like',
            'notify_on_mention', 'notify_on_new_follower',
            'notify_on_chat_request', 'notify_on_match_found',
            'show_spoilers', 'mature_content', 'preferred_language',
            'preferred_region', 'autoplay_trailers', 'theme_mode',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'updated_at']


class BlockedUserSerializer(serializers.ModelSerializer):
    """Serialize blocked users"""
    blocked_user_info = UserProfileSerializer(source='blocked_user', read_only=True)

    class Meta:
        model = BlockedUser
        fields = [
            'id', 'user', 'blocked_user', 'blocked_user_info',
            'reason', 'blocked_at'
        ]
        read_only_fields = ['id', 'user', 'blocked_at']


class ReportedUserSerializer(serializers.ModelSerializer):
    """Serialize reported users"""
    reporter_info = UserProfileSerializer(source='reporter', read_only=True)
    reported_user_info = UserProfileSerializer(source='reported_user', read_only=True)

    class Meta:
        model = ReportedUser
        fields = [
            'id', 'reporter', 'reporter_info', 'reported_user',
            'reported_user_info', 'reason', 'description',
            'status', 'admin_notes', 'reviewed_by', 'reviewed_at',
            'created_at'
        ]
        read_only_fields = ['id', 'reporter', 'created_at']


class PublicUserProfileSerializer(serializers.ModelSerializer):
    """Public-facing user profile (limited info)"""
    watch_time_display = serializers.CharField(source='get_watch_time_display', read_only=True)
    is_following = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'bio', 'profile_picture',
            'movies_watched_count', 'reviews_count', 'followers_count',
            'following_count', 'total_watch_time_minutes',
            'watch_time_display', 'created_at', 'is_following', 'is_blocked'
        ]
        read_only_fields = fields

    def get_is_following(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.authentication.models import UserFollow
            return UserFollow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        return False

    def get_is_blocked(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return BlockedUser.objects.filter(
                user=request.user,
                blocked_user=obj
            ).exists()
        return False

