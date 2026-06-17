from django.urls import path

from .views import (
    ActivePoliciesView,
    InsuranceProductListView,
    InsuranceSubscriptionListCreateView,
    ProcessInsuranceAlertsView,
)

urlpatterns = [
    path("products/", InsuranceProductListView.as_view(), name="insurance-products"),
    path("subscriptions/", InsuranceSubscriptionListCreateView.as_view(), name="insurance-subscriptions"),
    path("subscriptions/active/", ActivePoliciesView.as_view(), name="insurance-active"),
    path("process-alerts/", ProcessInsuranceAlertsView.as_view(), name="insurance-process-alerts"),
]
