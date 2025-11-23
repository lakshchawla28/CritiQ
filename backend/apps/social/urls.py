from django.urls import path
from .views import (
    SocialFeedView,
    UserAchievementsView,
    YearlyStatsView,
    GenerateYearlyWrapView,
)

urlpatterns = [
    # -----------------------------------
    # Social Feed
    # -----------------------------------
    path("feed/", SocialFeedView.as_view(), name="social-feed"),

    # -----------------------------------
    # User Achievements
    # -----------------------------------
    path("achievements/", UserAchievementsView.as_view(), name="user-achievements"),

    # -----------------------------------
    # Yearly Stats
    # -----------------------------------
    path("stats/<int:year>/", YearlyStatsView.as_view(), name="yearly-stats"),

    # -----------------------------------
    # Yearly Wrap (like Spotify Wrapped)
    # -----------------------------------
    path("wrap/<int:year>/", GenerateYearlyWrapView.as_view(), name="generate-wrap"),
]
