from django.urls import path
from .views import (
    GetRecommendationsView,
    GenerateRecommendationsView,
)

urlpatterns = [
    # Get personalized recommendations
    path("", GetRecommendationsView.as_view(), name="get-recommendations"),

    # Trigger manual regeneration
    path("generate/", GenerateRecommendationsView.as_view(), name="generate-recommendations"),
]
