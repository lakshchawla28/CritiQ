from django.urls import path
from .views import (
    RegisterView, VerifyOTPView, LoginView, SetUsernameView,
    ProfileView, UserDetailView, SendFollowRequestView,
    AcceptFollowRequestView, SendChatRequestView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('set-username/', SetUsernameView.as_view(), name='set-username'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('users/<str:username>/', UserDetailView.as_view(), name='user-detail'),
    path('follow/<uuid:user_id>/', SendFollowRequestView.as_view(), name='send-follow-request'),
    path('follow/accept/<uuid:request_id>/', AcceptFollowRequestView.as_view(), name='accept-follow'),
    path('chat-request/<uuid:user_id>/', SendChatRequestView.as_view(), name='send-chat-request'),
]