from django.urls import path
from .views import (
    SocialFeedView, UserAchievementsView, YearlyStatsView,
    GenerateYearlyWrapView
)

urlpatterns = [
    path('feed/', SocialFeedView.as_view(), name='social-feed'),
    path('achievements/', UserAchievementsView.as_view(), name='user-achievements'),
    path('stats/<int:year>/', YearlyStatsView.as_view(), name='yearly-stats'),
    path('wrap/<int:year>/', GenerateYearlyWrapView.as_view(), name='generate-wrap'),
]