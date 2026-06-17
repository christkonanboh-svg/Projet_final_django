from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AdminUserCreateView,
    ChangePasswordView,
    OnlineAgentsView,
    ProfileView,
    RegisterView,
    SetOnlineStatusView,
    UserListView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("me/", ProfileView.as_view(), name="auth-profile"),
    path("users/", UserListView.as_view(), name="auth-users-list"),
    path("users/create/", AdminUserCreateView.as_view(), name="auth-users-create"),
    path("agents/online/", OnlineAgentsView.as_view(), name="auth-agents-online"),
    path("online-status/", SetOnlineStatusView.as_view(), name="auth-online-status"),
    path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
]
