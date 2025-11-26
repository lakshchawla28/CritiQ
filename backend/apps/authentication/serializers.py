from rest_framework import serializers
from .models import User, OTPVerification, FollowRequest, ChatRequest
from django.contrib.auth.password_validation import validate_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User Registration Serializer"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'password_confirm', 'full_name']
        extra_kwargs = {
            'full_name': {'required': False}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        return user


class OTPVerifySerializer(serializers.Serializer):
    """OTP Verification Serializer"""
    phone_number = serializers.CharField()
    otp_code = serializers.CharField(max_length=6)

    # we attach otp_instance in validate for view
    def validate(self, data):
        try:
            otp = OTPVerification.objects.filter(
                phone_number=data['phone_number'],
                otp_code=data['otp_code'],
                is_verified=False
            ).latest('created_at')

            if otp.is_expired():
                raise serializers.ValidationError("OTP has expired")

            data['otp_instance'] = otp
            return data
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")


class LoginSerializer(serializers.Serializer):
    """Login Serializer"""
    identifier = serializers.CharField(help_text="Email, phone number, or username")
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class LoginResponseSerializer(serializers.Serializer):
    """Login Response Serializer"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']


class UserProfileSerializer(serializers.ModelSerializer):
    """User Profile Serializer"""
    watch_time_display = serializers.CharField(source='get_watch_time_display', read_only=True)
    is_following = serializers.SerializerMethodField()
    is_follower = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'username', 'full_name', 'bio',
            'profile_picture', 'date_of_birth', 'netflix_profile',
            'prime_video_profile', 'disney_plus_profile', 'hbo_max_profile',
            'reviews_privacy', 'ratings_privacy', 'watchlist_privacy',
            'watch_history_privacy', 'total_watch_time_minutes', 'watch_time_display',
            'movies_watched_count', 'reviews_count', 'followers_count',
            'following_count', 'friends_count', 'is_following', 'is_follower',
            'created_at'
        ]
        read_only_fields = [
            'id', 'email', 'phone_number', 'total_watch_time_minutes',
            'movies_watched_count', 'reviews_count', 'followers_count',
            'following_count', 'friends_count', 'created_at'
        ]

    def get_is_following(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import UserFollow
            return UserFollow.objects.filter(
                follower=request.user, following=obj
            ).exists()
        return False

    def get_is_follower(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import UserFollow
            return UserFollow.objects.filter(
                follower=obj, following=request.user
            ).exists()
        return False


class UsernameSetSerializer(serializers.Serializer):
    """Username Set Serializer"""
    username = serializers.CharField(max_length=30)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        if not value.replace('_', '').isalnum():
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores")
        return value


class FollowRequestSerializer(serializers.ModelSerializer):
    """Follow Request Serializer"""
    from_user = UserProfileSerializer(read_only=True)
    to_user = UserProfileSerializer(read_only=True)

    class Meta:
        model = FollowRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatRequestSerializer(serializers.ModelSerializer):
    """Chat Request Serializer"""
    from_user = UserProfileSerializer(read_only=True)
    to_user = UserProfileSerializer(read_only=True)

    class Meta:
        model = ChatRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# -------------------------
# Tiny helper serializers used for API docs
# -------------------------
class EmptySerializer(serializers.Serializer):
    """Used for endpoints that accept no request body (helps drf-spectacular)."""
    pass


class SendChatRequestCreateSerializer(serializers.Serializer):
    """Request body for sending a chat request (optional message)."""
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)


