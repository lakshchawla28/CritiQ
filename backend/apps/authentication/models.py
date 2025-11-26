"""
User Authentication Models
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """Custom user manager"""

    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not phone_number:
            raise ValueError('Phone number is required')

        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        if password is None:
            raise ValueError("Superuser must have a password")
        return self.create_user(email, phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True, db_index=True)

    # Profile Information
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.URLField(max_length=500, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # OTT Platform Links
    netflix_profile = models.URLField(max_length=200, blank=True, null=True)
    prime_video_profile = models.URLField(max_length=200, blank=True, null=True)
    disney_plus_profile = models.URLField(max_length=200, blank=True, null=True)
    hbo_max_profile = models.URLField(max_length=200, blank=True, null=True)

    # Privacy Settings
    PRIVACY_CHOICES = [
        ('everyone', 'Everyone'),
        ('followers', 'Followers Only'),
        ('friends', 'Friends Only'),
        ('private', 'Private'),
    ]

    reviews_privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='everyone')
    ratings_privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='everyone')
    watchlist_privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='friends')
    watch_history_privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='friends')

    # Account Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Stats (cached for performance)
    total_watch_time_minutes = models.IntegerField(default=0)
    movies_watched_count = models.IntegerField(default=0)
    reviews_count = models.IntegerField(default=0)
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    friends_count = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return self.username or self.email

    def get_watch_time_display(self):
        """Convert minutes to hours and minutes"""
        hours = self.total_watch_time_minutes // 60
        minutes = self.total_watch_time_minutes % 60
        return f"{hours}h {minutes}m"


class OTPVerification(models.Model):
    """OTP Verification Model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)

    VERIFICATION_TYPE_CHOICES = [
        ('registration', 'Registration'),
        ('login', 'Login'),
        ('phone_change', 'Phone Change'),
        ('email_change', 'Email Change'),
    ]
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPE_CHOICES)

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'otp_verifications'
        ordering = ['-created_at']

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.phone_number} - {self.verification_type}"


class FollowRequest(models.Model):
    """Follow/Friend Request Model"""

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_follow_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_follow_requests')

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'follow_requests'
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"


class UserFollow(models.Model):
    """User Follow Relationship (After request accepted)"""

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'user_follows'
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower} follows {self.following}"


class ChatRequest(models.Model):
    """Chat Request Model - Users need approval to chat"""

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_chat_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chat_requests')

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(max_length=200, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_requests'
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat request: {self.from_user} -> {self.to_user} ({self.status})"

