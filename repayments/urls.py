from django.urls import path

from .views import (
    CreditRepaymentHistoryView,
    ProcessAlertsView,
    RepaymentListCreateView,
    RepaymentScheduleListView,
)

urlpatterns = [
    path("", RepaymentListCreateView.as_view(), name="repayment-list-create"),
    path("schedules/", RepaymentScheduleListView.as_view(), name="repayment-schedules"),
    path("credit/<int:credit_id>/", CreditRepaymentHistoryView.as_view(), name="repayment-credit-history"),
    path("process-alerts/", ProcessAlertsView.as_view(), name="repayment-process-alerts"),
]
