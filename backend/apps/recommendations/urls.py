from django.urls import path
from .views import GetRecommendationsView, GenerateRecommendationsView

urlpatterns = [
    path('', GetRecommendationsView.as_view(), name='get-recommendations'),
    path('generate/', GenerateRecommendationsView.as_view(), name='generate-recommendations'),
]