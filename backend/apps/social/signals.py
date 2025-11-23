"""
Social Signals - Achievement Award Logic
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.movies.models import UserMovieInteraction
from apps.reviews.models import Review, ReviewLike
from apps.authentication.models import UserFollow
from .models import Achievement, UserAchievement


def check_and_award_achievement(user, achievement_name):
    """Helper function to award achievement if not already earned"""
    try:
        achievement = Achievement.objects.get(name=achievement_name)
        UserAchievement.objects.get_or_create(
            user=user,
            achievement=achievement,
            defaults={'progress': 100}
        )
    except Achievement.DoesNotExist:
        pass


@receiver(post_save, sender=UserMovieInteraction)
def check_watching_achievements(sender, instance, created, **kwargs):
    """Check and award achievements based on movies watched"""
    if instance.is_watched:
        user = instance.user
        movies_watched = UserMovieInteraction.objects.filter(
            user=user, is_watched=True
        ).count()
        
        # Award achievements based on watch count
        if movies_watched >= 1:
            check_and_award_achievement(user, "First Watch")
        if movies_watched >= 10:
            check_and_award_achievement(user, "Movie Buff")
        if movies_watched >= 50:
            check_and_award_achievement(user, "Cinephile")
        if movies_watched >= 100:
            check_and_award_achievement(user, "Century Club")
        if movies_watched >= 500:
            check_and_award_achievement(user, "Movie Master")
        if movies_watched >= 1000:
            check_and_award_achievement(user, "Legendary Viewer")


@receiver(post_save, sender=Review)
def check_reviewing_achievements(sender, instance, created, **kwargs):
    """Check and award achievements based on reviews written"""
    if created:
        user = instance.user
        reviews_count = Review.objects.filter(user=user).count()
        
        # Award achievements based on review count
        if reviews_count >= 1:
            check_and_award_achievement(user, "First Review")
        if reviews_count >= 10:
            check_and_award_achievement(user, "Critic")
        if reviews_count >= 50:
            check_and_award_achievement(user, "Pro Reviewer")
        if reviews_count >= 100:
            check_and_award_achievement(user, "Review Master")
        if reviews_count >= 500:
            check_and_award_achievement(user, "Legendary Critic")


@receiver(post_save, sender=ReviewLike)
def check_social_achievements(sender, instance, created, **kwargs):
    """Check achievements based on social interactions"""
    if created:
        # Check if review author reached milestones
        review_author = instance.review.user
        total_likes = ReviewLike.objects.filter(review__user=review_author).count()
        
        if total_likes >= 10:
            check_and_award_achievement(review_author, "Popular")
        if total_likes >= 100:
            check_and_award_achievement(review_author, "Influencer")
        if total_likes >= 1000:
            check_and_award_achievement(review_author, "Viral Star")


@receiver(post_save, sender=UserFollow)
def check_follower_achievements(sender, instance, created, **kwargs):
    """Check achievements based on followers"""
    if created:
        # Check achievements for the user being followed
        followed_user = instance.following
        followers_count = UserFollow.objects.filter(following=followed_user).count()
        
        if followers_count >= 10:
            check_and_award_achievement(followed_user, "Rising Star")
        if followers_count >= 50:
            check_and_award_achievement(followed_user, "Community Leader")
        if followers_count >= 100:
            check_and_award_achievement(followed_user, "Celebrity")
        if followers_count >= 1000:
            check_and_award_achievement(followed_user, "Icon")