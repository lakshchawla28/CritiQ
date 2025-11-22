from celery import shared_task
from apps.authentication.models import User
from .recommendation_engine import RecommendationEngine

@shared_task
def generate_recommendations_for_user(user_id):
    """Background task to generate recommendations"""
    try:
        user = User.objects.get(id=user_id)
        engine = RecommendationEngine(user)
        engine.generate_recommendations()
        return f"Generated recommendations for {user.username}"
    except User.DoesNotExist:
        return f"User {user_id} not found"

@shared_task
def generate_all_recommendations():
    """Generate recommendations for all active users"""
    users = User.objects.filter(is_active=True, is_verified=True)
    for user in users:
        generate_recommendations_for_user.delay(str(user.id))
    return f"Queued recommendations for {users.count()} users"
