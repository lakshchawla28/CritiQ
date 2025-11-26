from django.urls import path
from .views import (
    UserStatsView,
    UserActivityListView,
    UserPreferencesView,
    BlockUserView,
    UnblockUserView,
    BlockedUsersListView,
    ReportUserView,
    SearchUsersView,
    TopUsersView,
)

urlpatterns = [
    # Stats
    path("stats/", UserStatsView.as_view(), name="user-stats-self"),
    path("stats/<uuid:user_id>/", UserStatsView.as_view(), name="user-stats-other"),

    # Activity
    path("activity/", UserActivityListView.as_view(), name="user-activity-self"),
    path("activity/<uuid:user_id>/", UserActivityListView.as_view(), name="user-activity-other"),

    # Preferences
    path("preferences/", UserPreferencesView.as_view(), name="user-preferences"),

    # Block / Unblock
    path("block/<uuid:user_id>/", BlockUserView.as_view(), name="block-user"),
    path("unblock/<uuid:user_id>/", UnblockUserView.as_view(), name="unblock-user"),
    path("blocked/", BlockedUsersListView.as_view(), name="blocked-users"),

    # Reporting
    path("report/<uuid:user_id>/", ReportUserView.as_view(), name="report-user"),

    # Discovery
    path("search/", SearchUsersView.as_view(), name="search-users"),
    path("top/", TopUsersView.as_view(), name="top-users"),
]
