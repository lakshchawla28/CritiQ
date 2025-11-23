from celery import shared_task
from .ml.engine import RecommendationEngine


@shared_task
def generate_recommendations_task():
    """
    Regenerate ALL recommendations.
    """
    engine = RecommendationEngine()
    engine.generate_recommendations_for_all()
    return "All recommendations regenerated"


@shared_task
def generate_recommendations_for_user(user_id):
    """
    Generate recommendations ONLY for a single user.
    """
    from apps.authentication.models import User
    engine = RecommendationEngine()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"User {user_id} does not exist"

    recs = engine.recommend_for_user(user)
    engine.save_user_recommendations(user, recs)

    return f"Recommendations regenerated for user {user_id}"


