from django.urls import path
from .views import (
    RegisterView,
    VerifyOTPView,
    LoginView,
    SetUsernameView,
    ProfileView,
    UserDetailView,
    SendFollowRequestView,
    AcceptFollowRequestView,
    SendChatRequestView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # --- Authentication & OTP ---
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # --- User Setup ---
    path("set-username/", SetUsernameView.as_view(), name="set-username"),
    path("profile/", ProfileView.as_view(), name="profile"),

    # --- User Data ---
    path("users/<str:username>/", UserDetailView.as_view(), name="user-detail"),

    # --- Social: Follow ---
    path("follow/<uuid:user_id>/", SendFollowRequestView.as_view(), name="send-follow-request"),
    path("follow/accept/<uuid:request_id>/", AcceptFollowRequestView.as_view(), name="accept-follow"),

    # --- Chat: Chat Requests ---
    path("chat-request/<uuid:user_id>/", SendChatRequestView.as_view(), name="send-chat-request"),
]
