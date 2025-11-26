# apps/authentication/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

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

# Namespace for cleaner routing and to avoid conflicts
app_name = "authentication"

urlpatterns = [
    # ============================================
    # AUTHENTICATION & OTP
    # ============================================
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # ============================================
    # USER ACCOUNT SETUP
    # ============================================
    path("set-username/", SetUsernameView.as_view(), name="set-username"),
    path("profile/", ProfileView.as_view(), name="profile"),

    # ============================================
    # USER PUBLIC DATA
    # ============================================
    path("user/<str:username>/", UserDetailView.as_view(), name="user-detail"),

    # ============================================
    # SOCIAL: FOLLOW / UNFOLLOW
    # ============================================
    path("follow/<uuid:user_id>/", SendFollowRequestView.as_view(), name="send-follow-request"),
    path("follow/accept/<uuid:request_id>/", AcceptFollowRequestView.as_view(), name="accept-follow"),

    # ============================================
    # SOCIAL: CHAT REQUESTS
    # ============================================
    path("chat-request/<uuid:user_id>/", SendChatRequestView.as_view(), name="send-chat-request"),
]
