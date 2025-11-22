"""
Social Feed & Activity Models
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
from apps.reviews.models import Review
import uuid

class Post(models.Model):
    """Social Feed Post (can be standalone or linked to review)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    # Post content
    content = models.TextField(max_length=2000, blank=True)
    
    # Linked content
    review = models.ForeignKey(Review, null=True, blank=True, on_delete=models.CASCADE, related_name='posts')
    
    # Stats
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.user}"


class Achievement(models.Model):
    """Achievement/Badge System"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500)
    icon = models.CharField(max_length=50)  # Icon identifier
    
    # Achievement criteria (stored as JSON)
    criteria = models.JSONField()
    
    # Categories
    CATEGORY_CHOICES = [
        ('watching', 'Watching'),
        ('reviewing', 'Reviewing'),
        ('social', 'Social'),
        ('seasonal', 'Seasonal'),
        ('special', 'Special'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Rarity
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    
    points = models.IntegerField(default=10)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'achievements'
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """User's Earned Achievements"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    
    earned_at = models.DateTimeField(default=timezone.now)
    progress = models.IntegerField(default=100)  # Percentage of completion
    
    class Meta:
        db_table = 'user_achievements'
        unique_together = ('user', 'achievement')
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user} earned {self.achievement.name}"


class YearlyStats(models.Model):
    """Yearly Statistics for Wrap-up"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='yearly_stats')
    year = models.IntegerField()
    
    # Watching stats
    movies_watched = models.IntegerField(default=0)
    total_runtime_minutes = models.IntegerField(default=0)
    top_genres = models.JSONField(default=list)
    top_rated_movies = models.JSONField(default=list)
    
    # Review stats
    reviews_written = models.IntegerField(default=0)
    avg_rating_given = models.FloatField(default=0)
    most_used_tags = models.JSONField(default=list)
    
    # Social stats
    new_followers = models.IntegerField(default=0)
    likes_received = models.IntegerField(default=0)
    
    # Achievements
    badges_earned = models.JSONField(default=list)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'yearly_stats'
        unique_together = ('user', 'year')
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.user} - {self.year} Stats"