from django.urls import path

from .views import (
    CreditDetailView,
    CreditDocumentUploadView,
    CreditEligibilityScoreView,
    CreditListCreateView,
    CreditScheduleView,
    CreditStatusUpdateView,
)

urlpatterns = [
    path("", CreditListCreateView.as_view(), name="credit-list-create"),
    path("<int:pk>/", CreditDetailView.as_view(), name="credit-detail"),
    path("<int:pk>/status/", CreditStatusUpdateView.as_view(), name="credit-status"),
    path("<int:pk>/eligibility-score/", CreditEligibilityScoreView.as_view(), name="credit-eligibility"),
    path("<int:pk>/schedule/", CreditScheduleView.as_view(), name="credit-schedule"),
    path("<int:pk>/documents/", CreditDocumentUploadView.as_view(), name="credit-documents"),
]
