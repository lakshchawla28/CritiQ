"""
Review Signals - Update stats and trigger achievements
"""

from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Review, ReviewLike, ReviewComment, ReviewRepost, Tag


@receiver(post_save, sender=ReviewLike)
def update_review_likes_count_on_save(sender, instance, created, **kwargs):
    """Update review likes count when a like is added"""
    if created:
        review = instance.review
        review.likes_count = review.likes.count()
        review.save(update_fields=['likes_count'])


@receiver(post_delete, sender=ReviewLike)
def update_review_likes_count_on_delete(sender, instance, **kwargs):
    """Update review likes count when a like is removed"""
    review = instance.review
    review.likes_count = review.likes.count()
    review.save(update_fields=['likes_count'])


@receiver(post_save, sender=ReviewComment)
def update_review_comments_count_on_save(sender, instance, created, **kwargs):
    """Update review comments count when a comment is added"""
    if created:
        review = instance.review
        review.comments_count = review.comments.count()
        review.save(update_fields=['comments_count'])


@receiver(post_delete, sender=ReviewComment)
def update_review_comments_count_on_delete(sender, instance, **kwargs):
    """Update review comments count when a comment is removed"""
    review = instance.review
    review.comments_count = review.comments.count()
    review.save(update_fields=['comments_count'])


@receiver(post_save, sender=ReviewRepost)
def update_review_reposts_count_on_save(sender, instance, created, **kwargs):
    """Update review reposts count when a repost is added"""
    if created:
        review = instance.original_review
        review.reposts_count = review.reposts.count()
        review.save(update_fields=['reposts_count'])


@receiver(post_delete, sender=ReviewRepost)
def update_review_reposts_count_on_delete(sender, instance, **kwargs):
    """Update review reposts count when a repost is removed"""
    review = instance.original_review
    review.reposts_count = review.reposts.count()
    review.save(update_fields=['reposts_count'])


@receiver(m2m_changed, sender=Review.tags.through)
def update_tag_usage_count(sender, instance, action, **kwargs):
    """Update tag usage counts when tags are added/removed"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Get all tags that were affected
        if action == 'post_clear':
            tags = Tag.objects.all()
        else:
            pk_set = kwargs.get('pk_set', [])
            tags = Tag.objects.filter(pk__in=pk_set)
        
        # Update usage count for each tag
        for tag in tags:
            tag.usage_count = tag.reviews.count()
            tag.save(update_fields=['usage_count'])


@receiver(post_save, sender=Review)
def update_user_review_count(sender, instance, created, **kwargs):
    """Update user's total review count"""
    if created:
        user = instance.user
        user.reviews_count = user.reviews.count()
        user.save(update_fields=['reviews_count'])


@receiver(post_delete, sender=Review)
def update_user_review_count_on_delete(sender, instance, **kwargs):
    """Update user's total review count when review is deleted"""
    user = instance.user
    user.reviews_count = user.reviews.count()
    user.save(update_fields=['reviews_count'])