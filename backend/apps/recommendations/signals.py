from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.movies.models import UserMovieInteraction
from .tasks import generate_recommendations_for_user

@receiver(post_save, sender=UserMovieInteraction)
def trigger_recommendation_refresh(sender, instance, **kwargs):
    """
    When a user interacts with a movie -> generate recommendations for that user
    """
    generate_recommendations_for_user.delay(instance.user_id)

