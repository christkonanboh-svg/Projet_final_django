from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.views.generic import TemplateView
from frontend_views import (
    AdminAgentsView, AdminChatView, AdminCreditsView, AdminDashboardView,
    AdminInsuranceView, AdminNotificationsView, AdminProfileView,
    AdminRepaymentsView, AdminUsersView,
    AgentChatView, AgentCreditsView, AgentDashboardView,
    AgentInsuranceView, AgentNotificationsView, AgentProfileView,
    AgentRepaymentsView,
    AppIndexView, AppLoginView, AppRegisterView,
    ClientChatView, ClientCreditsView, ClientDashboardView, ClientInsuranceView,
    ClientNotificationsView, ClientProfileView, ClientRepaymentsView,
)

urlpatterns = [
    path("", AppIndexView.as_view(), name="app-index"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/auth/", include("accounts.urls")),
    path("api/credits/", include("credits.urls")),
    path("api/repayments/", include("repayments.urls")),
    path("api/insurance/", include("insurance.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/chat/", include("chat.urls")),
    path("chat/", RedirectView.as_view(url="/app/client/chat/", permanent=False), name="chat-index"),
    path("chat/client/", RedirectView.as_view(url="/app/client/chat/", permanent=False), name="chat-client"),
    path("chat/agent/", RedirectView.as_view(url="/app/agent/chat/", permanent=False), name="chat-agent"),
    # Auth
    path("app/login/", AppLoginView.as_view(), name="app-login"),
    path("app/register/", AppRegisterView.as_view(), name="app-register"),
    # Client
    path("app/client/dashboard/", ClientDashboardView.as_view(), name="client-dashboard"),
    path("app/client/credits/", ClientCreditsView.as_view(), name="client-credits"),
    path("app/client/insurance/", ClientInsuranceView.as_view(), name="client-insurance"),
    path("app/client/repayments/", ClientRepaymentsView.as_view(), name="client-repayments"),
    path("app/client/chat/", ClientChatView.as_view(), name="client-chat"),
    path("app/client/notifications/", ClientNotificationsView.as_view(), name="client-notifications"),
    path("app/client/profile/", ClientProfileView.as_view(), name="client-profile"),
    # Agent
    path("app/agent/dashboard/", AgentDashboardView.as_view(), name="agent-dashboard"),
    path("app/agent/credits/", AgentCreditsView.as_view(), name="agent-credits"),
    path("app/agent/insurance/", AgentInsuranceView.as_view(), name="agent-insurance"),
    path("app/agent/repayments/", AgentRepaymentsView.as_view(), name="agent-repayments"),
    path("app/agent/chat/", AgentChatView.as_view(), name="agent-chat"),
    path("app/agent/notifications/", AgentNotificationsView.as_view(), name="agent-notifications"),
    path("app/agent/profile/", AgentProfileView.as_view(), name="agent-profile"),
    # Admin
    path("app/admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("app/admin/credits/", AdminCreditsView.as_view(), name="admin-credits"),
    path("app/admin/users/", AdminUsersView.as_view(), name="admin-users"),
    path("app/admin/chat/", AdminChatView.as_view(), name="admin-chat"),
    path("app/admin/insurance/", AdminInsuranceView.as_view(), name="admin-insurance"),
    path("app/admin/agents/", AdminAgentsView.as_view(), name="admin-agents"),
    path("app/admin/repayments/", AdminRepaymentsView.as_view(), name="admin-repayments"),
    path("app/admin/notifications/", AdminNotificationsView.as_view(), name="admin-notifications"),
    path("app/admin/profile/", AdminProfileView.as_view(), name="admin-profile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()