"""
User Signals - Update user stats and handle blocking
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.authentication.models import UserFollow, User
from apps.movies.models import UserMovieInteraction
from apps.reviews.models import Review, ReviewLike
from .models import BlockedUser, UserStats
from django.utils import timezone


@receiver(post_save, sender=UserFollow)
def update_follow_counts_on_save(sender, instance, created, **kwargs):
    """Update follower/following counts when a follow relationship is created"""
    if created:
        following_user = instance.following
        follower_user = instance.follower

        # update follower count
        following_user.followers_count = following_user.followers.count()
        following_user.save(update_fields=['followers_count'])

        # update following count
        follower_user.following_count = follower_user.following.count()
        follower_user.save(update_fields=['following_count'])


@receiver(post_delete, sender=UserFollow)
def update_follow_counts_on_delete(sender, instance, **kwargs):
    """Update follower/following counts when a follow relationship is deleted"""
    following_user = instance.following
    follower_user = instance.follower

    following_user.followers_count = following_user.followers.count()
    following_user.save(update_fields=['followers_count'])

    follower_user.following_count = follower_user.following.count()
    follower_user.save(update_fields=['following_count'])


@receiver(post_save, sender=UserMovieInteraction)
def update_user_watch_stats(sender, instance, created, **kwargs):
    """
    Update user watch stats when they watch a movie.
    This keeps the User model counters and UserStats in sync.
    """
    if instance.is_watched and instance.watched_date:
        user = instance.user

        # Update movies watched count on user model
        total_watched = UserMovieInteraction.objects.filter(user=user, is_watched=True).count()
        user.movies_watched_count = total_watched

        # Update total watch time (sum runtimes)
        watched_movies = UserMovieInteraction.objects.filter(user=user, is_watched=True).select_related('movie')
        total_runtime = sum((i.movie.runtime or 0) for i in watched_movies if getattr(i, 'movie', None))
        user.total_watch_time_minutes = total_runtime

        user.save(update_fields=['movies_watched_count', 'total_watch_time_minutes'])

        # Update UserStats
        user_stats, _ = UserStats.objects.get_or_create(user=user)
        today = timezone.now().date()

        if user_stats.last_watch_date:
            days_diff = (today - user_stats.last_watch_date).days
            if days_diff == 0:
                # same day -> don't increment
                pass
            elif days_diff == 1:
                user_stats.current_watch_streak += 1
                if user_stats.current_watch_streak > user_stats.longest_watch_streak:
                    user_stats.longest_watch_streak = user_stats.current_watch_streak
            else:
                user_stats.current_watch_streak = 1
        else:
            user_stats.current_watch_streak = 1
            user_stats.longest_watch_streak = max(user_stats.longest_watch_streak, 1)

        user_stats.last_watch_date = today
        user_stats.save()


@receiver(post_save, sender=BlockedUser)
def handle_user_block(sender, instance, created, **kwargs):
    """Handle consequences of blocking a user (remove follows)."""
    if created:
        blocker = instance.user
        blocked = instance.blocked_user

        # Remove follow relationships
        UserFollow.objects.filter(follower=blocker, following=blocked).delete()
        UserFollow.objects.filter(follower=blocked, following=blocker).delete()


@receiver(post_save, sender=User)
def create_user_stats(sender, instance, created, **kwargs):
    """Create UserStats when a new user is created"""
    if created:
        UserStats.objects.get_or_create(user=instance)
