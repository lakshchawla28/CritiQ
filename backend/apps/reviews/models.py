"""
Reviews App Models
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
from apps.movies.models import Movie
import uuid


class Tag(models.Model):
    """Predefined tags for reviews"""
    
    name = models.CharField(max_length=50, unique=True)
    
    CATEGORY_CHOICES = [
        ('mood', 'Mood'),
        ('pace', 'Pace'),
        ('quality', 'Quality'),
        ('theme', 'Theme'),
        ('general', 'General'),
    ]
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Review(models.Model):
    """Movie Review Model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    
    # Rating (same 4-tier system)
    RATING_CHOICES = [
        ('trash', 'Trash'),
        ('timepass', 'Timepass'),
        ('worth', 'Worth the Clock'),
        ('peak', 'Peak'),
    ]
    rating = models.CharField(max_length=20, choices=RATING_CHOICES, null=True, blank=True)
    
    # Review Content
    review_text = models.TextField(max_length=5000, blank=True)
    contains_spoilers = models.BooleanField(default=False)
    
    # Tags - NOW ManyToMany
    tags = models.ManyToManyField(Tag, related_name='reviews', blank=True)
    
    # Privacy
    PRIVACY_CHOICES = [
        ('everyone', 'Everyone'),
        ('followers', 'Followers Only'),
        ('friends', 'Friends Only'),
        ('private', 'Private'),
    ]
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='everyone')
    
    # Stats
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    reposts_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ('user', 'movie')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['movie']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Review by {self.user} on {self.movie}"


class ReviewLike(models.Model):
    """Review Likes"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_likes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'review_likes'
        unique_together = ('user', 'review')
    
    def __str__(self):
        return f"{self.user} liked review {self.review.id}"


class ReviewComment(models.Model):
    """Comments on Reviews"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_comments')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    
    comment_text = models.TextField(max_length=1000)
    
    # Reply structure
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'review_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user} on review {self.review.id}"


class ReviewRepost(models.Model):
    """Repost Reviews (like Twitter retweet)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_reposts')
    original_review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reposts')
    
    # User can add their own comment when reposting
    comment = models.TextField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'review_reposts'
        unique_together = ('user', 'original_review')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} reposted review {self.original_review.id}"