from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.recommendations.models import Recommendation
from apps.recommendations.serializers import RecommendationSerializer
from apps.recommendations.tasks import (
    generate_recommendations_for_user,
    generate_recommendations_task,
)


# ======================================================
#   GET RECOMMENDATIONS
# ======================================================

class GetRecommendationsView(generics.ListAPIView):
    """
    Returns personalized recommendations for the logged-in user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RecommendationSerializer

    def get_queryset(self):
        return Recommendation.objects.filter(
            user=self.request.user,
            is_dismissed=False
        ).order_by("-score", "-created_at")


# ======================================================
#   GENERATE RECOMMENDATIONS (Manual Trigger)
# ======================================================

class GenerateRecommendationsView(generics.GenericAPIView):
    """
    Triggers recommendation generation for:
    - current user (user=me)
    - all users (default)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target = request.query_params.get("user")

        # Generate for current logged-in user
        if target == "me":
            generate_recommendations_for_user.delay(str(request.user.id))
            return Response(
                {"message": "Generating fresh recommendations for you..."},
                status=status.HTTP_200_OK,
            )

        # Generate for everyone
        generate_recommendations_task.delay()

        return Response(
            {"message": "Regenerating recommendations for all users..."},
            status=status.HTTP_200_OK,
        )
