from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAgentOrAdmin, IsClient
from notifications.services import create_notification
from repayments.serializers import RepaymentScheduleSerializer

from rest_framework import serializers

from .models import CreditApplication, CreditDocument, calculate_eligibility_score, generate_repayment_schedule
from .serializers import (
    CreditApplicationSerializer,
    CreditCreateSerializer,
    CreditDocumentUploadSerializer,
    CreditStatusUpdateSerializer,
)


class EligibilityScoreSerializer(serializers.Serializer):
    credit_id = serializers.IntegerField()
    eligibility_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    eligible = serializers.BooleanField()


class CreditListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreditCreateSerializer
        return CreditApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        qs = CreditApplication.objects.select_related("client", "assigned_agent").prefetch_related("documents")
        if user.is_client:
            return qs.filter(client=user)
        if user.is_agent:
            return qs.filter(assigned_agent=user) | qs.filter(status=CreditApplication.Status.SUBMITTED)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_client:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les clients peuvent soumettre une demande de crédit.")
        score = calculate_eligibility_score(user, serializer.validated_data["amount_requested"])
        credit = serializer.save(
            client=user,
            eligibility_score=score,
            region=serializer.validated_data.get("region") or user.region,
        )
        create_notification(
            user,
            "Demande de crédit soumise",
            f"Votre demande de {credit.amount_requested} FCFA a été enregistrée.",
            "credit_submitted",
            {"credit_id": credit.id},
        )


class CreditDetailView(generics.RetrieveAPIView):
    serializer_class = CreditApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = CreditApplication.objects.select_related("client", "assigned_agent").prefetch_related("documents")
        if user.is_client:
            return qs.filter(client=user)
        return qs


class CreditStatusUpdateView(APIView):
    permission_classes = [IsAgentOrAdmin]

    @extend_schema(request=CreditStatusUpdateSerializer, responses={200: CreditApplicationSerializer})
    def patch(self, request, pk):
        try:
            credit = CreditApplication.objects.get(pk=pk)
        except CreditApplication.DoesNotExist:
            return Response({"detail": "Crédit introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreditStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        old_status = credit.status

        valid_transitions = {
            CreditApplication.Status.SUBMITTED: [CreditApplication.Status.IN_REVIEW, CreditApplication.Status.REJECTED],
            CreditApplication.Status.IN_REVIEW: [CreditApplication.Status.APPROVED, CreditApplication.Status.REJECTED],
            CreditApplication.Status.APPROVED: [CreditApplication.Status.DISBURSED],
        }
        if new_status not in valid_transitions.get(old_status, []) and new_status != old_status:
            return Response(
                {"detail": f"Transition invalide de {old_status} vers {new_status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        credit.status = new_status
        if "assigned_agent" in serializer.validated_data:
            credit.assigned_agent = serializer.validated_data["assigned_agent"]
        if new_status == CreditApplication.Status.REJECTED:
            credit.rejection_reason = serializer.validated_data.get("rejection_reason", "")
        if new_status == CreditApplication.Status.APPROVED:
            credit.approved_at = timezone.now()
            generate_repayment_schedule(credit)
        if new_status == CreditApplication.Status.DISBURSED:
            credit.disbursed_at = timezone.now()

        credit.save()
        create_notification(
            credit.client,
            "Mise à jour de votre crédit",
            f"Votre demande est maintenant : {credit.get_status_display()}.",
            "credit_status",
            {"credit_id": credit.id, "status": new_status},
        )
        return Response(CreditApplicationSerializer(credit).data)


class CreditEligibilityScoreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EligibilityScoreSerializer

    @extend_schema(responses={200: EligibilityScoreSerializer})
    def get(self, request, pk):
        try:
            credit = CreditApplication.objects.get(pk=pk)
        except CreditApplication.DoesNotExist:
            return Response({"detail": "Crédit introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_client and credit.client != request.user:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "credit_id": credit.id,
            "eligibility_score": credit.eligibility_score,
            "eligible": credit.eligibility_score >= 60,
        })


class CreditScheduleView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RepaymentScheduleSerializer

    @extend_schema(responses={200: RepaymentScheduleSerializer(many=True)})
    def get(self, request, pk):
        try:
            credit = CreditApplication.objects.get(pk=pk)
        except CreditApplication.DoesNotExist:
            return Response({"detail": "Crédit introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_client and credit.client != request.user:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        schedules = credit.schedules.all()
        return Response(RepaymentScheduleSerializer(schedules, many=True).data)


class CreditDocumentUploadView(generics.CreateAPIView):
    serializer_class = CreditDocumentUploadSerializer
    permission_classes = [IsClient]

    def perform_create(self, serializer):
        credit_id = self.kwargs["pk"]
        credit = CreditApplication.objects.get(pk=credit_id, client=self.request.user)
        serializer.save(credit=credit)
