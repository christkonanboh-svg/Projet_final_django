from django.views.generic import TemplateView


class AppLoginView(TemplateView):
    template_name = "app/login.html"


# Client
class ClientDashboardView(TemplateView):
    template_name = "app/client/dashboard.html"


class ClientCreditsView(TemplateView):
    template_name = "app/client/credits.html"


class ClientInsuranceView(TemplateView):
    template_name = "app/client/insurance.html"


class ClientRepaymentsView(TemplateView):
    template_name = "app/client/repayments.html"


class ClientChatView(TemplateView):
    template_name = "app/client/chat.html"


class ClientNotificationsView(TemplateView):
    template_name = "app/client/notifications.html"


class ClientProfileView(TemplateView):
    template_name = "app/client/profile.html"


# Agent
class AgentDashboardView(TemplateView):
    template_name = "app/agent/dashboard.html"


class AgentCreditsView(TemplateView):
    template_name = "app/agent/credits.html"


class AgentChatView(TemplateView):
    template_name = "app/agent/chat.html"


class AgentNotificationsView(TemplateView):
    template_name = "app/agent/notifications.html"


class AgentProfileView(TemplateView):
    template_name = "app/agent/profile.html"


# Admin
class AdminDashboardView(TemplateView):
    template_name = "app/admin/dashboard.html"


class AdminCreditsView(TemplateView):
    template_name = "app/admin/credits.html"


class AdminUsersView(TemplateView):
    template_name = "app/admin/users.html"


class AdminChatView(TemplateView):
    template_name = "app/admin/chat.html"


class AdminInsuranceView(TemplateView):
    template_name = "app/admin/insurance.html"


class AdminAgentsView(TemplateView):
    template_name = "app/admin/agents.html"


class AdminNotificationsView(TemplateView):
    template_name = "app/admin/notifications.html"


class AdminProfileView(TemplateView):
    template_name = "app/admin/profile.html"
