from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAgentOrAdmin
from notifications.services import create_notification

from .models import Repayment, RepaymentSchedule
from .serializers import RepaymentCreateSerializer, RepaymentScheduleSerializer, RepaymentSerializer
from .services import process_repayment_alerts


class RepaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RepaymentCreateSerializer
        return RepaymentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Repayment.objects.select_related("schedule__credit__client", "recorded_by")
        if user.is_client:
            return qs.filter(schedule__credit__client=user)
        return qs

    def perform_create(self, serializer):
        if not (self.request.user.is_agent or self.request.user.is_admin_user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les agents peuvent enregistrer un paiement.")
        repayment = serializer.save(recorded_by=self.request.user)
        client = repayment.schedule.credit.client
        create_notification(
            client,
            "Remboursement enregistré",
            f"Paiement de {repayment.amount} FCFA enregistré pour l'échéance "
            f"n°{repayment.schedule.installment_number}.",
            "repayment_recorded",
            {"repayment_id": repayment.id, "credit_id": repayment.schedule.credit_id},
        )


class RepaymentScheduleListView(generics.ListAPIView):
    serializer_class = RepaymentScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = RepaymentSchedule.objects.select_related("credit")
        if user.is_client:
            return qs.filter(credit__client=user)
        credit_id = self.request.query_params.get("credit_id")
        if credit_id:
            return qs.filter(credit_id=credit_id)
        return qs


class CreditRepaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: RepaymentSerializer(many=True)})
    def get(self, request, credit_id):
        repayments = Repayment.objects.filter(schedule__credit_id=credit_id).select_related(
            "schedule", "recorded_by"
        )
        if request.user.is_client:
            repayments = repayments.filter(schedule__credit__client=request.user)
        return Response(RepaymentSerializer(repayments, many=True).data)


class ProcessAlertsView(APIView):
    permission_classes = [IsAgentOrAdmin]
    serializer_class = None

    @extend_schema(
        request=None,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        process_repayment_alerts()
        return Response({"detail": "Alertes de remboursement traitées."})
