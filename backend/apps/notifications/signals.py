"""
Notification Signals - Auto-create notifications on events
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.authentication.models import FollowRequest, ChatRequest, UserFollow
from apps.reviews.models import ReviewLike, ReviewComment, ReviewRepost
from apps.social.models import UserAchievement
from apps.matching.models import MatchResult
from .models import Notification


@receiver(post_save, sender=FollowRequest)
def notify_follow_request(sender, instance, created, **kwargs):
    """Notify user when they receive a follow request"""
    if created and instance.status == 'pending':
        Notification.objects.create(
            user=instance.to_user,
            notification_type='follow_request',
            title='New Follow Request',
            message=f'{instance.from_user.username} wants to follow you',
            related_user=instance.from_user,
            related_object_id=str(instance.id),
            related_object_type='follow_request',
            action_url=f'/profile/{instance.from_user.username}'
        )
    
    # Notify when request is accepted
    elif instance.status == 'accepted':
        Notification.objects.create(
            user=instance.from_user,
            notification_type='follow_accepted',
            title='Follow Request Accepted',
            message=f'{instance.to_user.username} accepted your follow request',
            related_user=instance.to_user,
            related_object_id=str(instance.id),
            related_object_type='follow_request',
            action_url=f'/profile/{instance.to_user.username}'
        )


@receiver(post_save, sender=UserFollow)
def notify_new_follower(sender, instance, created, **kwargs):
    """Notify user when someone follows them"""
    if created:
        Notification.objects.create(
            user=instance.following,
            notification_type='new_follower',
            title='New Follower',
            message=f'{instance.follower.username} started following you',
            related_user=instance.follower,
            related_object_id=str(instance.id),
            related_object_type='follow',
            action_url=f'/profile/{instance.follower.username}'
        )


@receiver(post_save, sender=ChatRequest)
def notify_chat_request(sender, instance, created, **kwargs):
    """Notify user about chat requests"""
    if created and instance.status == 'pending':
        Notification.objects.create(
            user=instance.to_user,
            notification_type='chat_request',
            title='New Chat Request',
            message=f'{instance.from_user.username} wants to chat with you',
            related_user=instance.from_user,
            related_object_id=str(instance.id),
            related_object_type='chat_request',
            action_url='/chat/requests'
        )
    
    elif instance.status == 'accepted':
        Notification.objects.create(
            user=instance.from_user,
            notification_type='chat_accepted',
            title='Chat Request Accepted',
            message=f'{instance.to_user.username} accepted your chat request',
            related_user=instance.to_user,
            related_object_id=str(instance.id),
            related_object_type='chat_request',
            action_url='/chat'
        )


@receiver(post_save, sender=ReviewLike)
def notify_review_like(sender, instance, created, **kwargs):
    """Notify user when their review is liked"""
    if created and instance.review.user != instance.user:
        Notification.objects.create(
            user=instance.review.user,
            notification_type='review_liked',
            title='Review Liked',
            message=f'{instance.user.username} liked your review',
            related_user=instance.user,
            related_object_id=str(instance.review.id),
            related_object_type='review',
            action_url=f'/reviews/{instance.review.id}'
        )


@receiver(post_save, sender=ReviewComment)
def notify_review_comment(sender, instance, created, **kwargs):
    """Notify user when someone comments on their review"""
    if created and instance.review.user != instance.user:
        Notification.objects.create(
            user=instance.review.user,
            notification_type='review_commented',
            title='New Comment',
            message=f'{instance.user.username} commented on your review',
            related_user=instance.user,
            related_object_id=str(instance.review.id),
            related_object_type='review',
            action_url=f'/reviews/{instance.review.id}'
        )


@receiver(post_save, sender=ReviewRepost)
def notify_review_repost(sender, instance, created, **kwargs):
    """Notify user when their review is reposted"""
    if created and instance.original_review.user != instance.user:
        Notification.objects.create(
            user=instance.original_review.user,
            notification_type='review_reposted',
            title='Review Reposted',
            message=f'{instance.user.username} reposted your review',
            related_user=instance.user,
            related_object_id=str(instance.original_review.id),
            related_object_type='review',
            action_url=f'/reviews/{instance.original_review.id}'
        )


@receiver(post_save, sender=UserAchievement)
def notify_achievement_earned(sender, instance, created, **kwargs):
    """Notify user when they earn an achievement"""
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type='achievement_earned',
            title='Achievement Unlocked! 🏆',
            message=f'You earned "{instance.achievement.name}"',
            related_object_id=str(instance.achievement.id),
            related_object_type='achievement',
            action_url='/profile/achievements'
        )


@receiver(post_save, sender=MatchResult)
def notify_match_found(sender, instance, created, **kwargs):
    """Notify all participants when a match is found"""
    if created:
        for user in instance.matched_users.all():
            Notification.objects.create(
                user=user,
                notification_type='match_found',
                title='Movie Match Found! 🎬',
                message=f'You matched on "{instance.movie.title}"',
                related_object_id=str(instance.session.id),
                related_object_type='matching_session',
                action_url=f'/matching/{instance.session.id}'
            )