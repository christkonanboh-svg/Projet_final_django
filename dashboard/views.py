from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminUser
from chat.models import Conversation
from credits.models import CreditApplication
from insurance.models import InsuranceSubscription
from repayments.models import RepaymentSchedule


class DashboardStatsView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = None

    @extend_schema(
        parameters=[
            OpenApiParameter("date_from", str, description="Date début (YYYY-MM-DD)"),
            OpenApiParameter("date_to", str, description="Date fin (YYYY-MM-DD)"),
            OpenApiParameter("agent", int, description="ID agent"),
            OpenApiParameter("region", str, description="Région"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        agent_id = request.query_params.get("agent")
        region = request.query_params.get("region")

        credits_qs = CreditApplication.objects.all()
        if date_from:
            credits_qs = credits_qs.filter(submitted_at__date__gte=date_from)
        if date_to:
            credits_qs = credits_qs.filter(submitted_at__date__lte=date_to)
        if agent_id:
            credits_qs = credits_qs.filter(assigned_agent_id=agent_id)
        if region:
            credits_qs = credits_qs.filter(region=region)

        credits_by_status = dict(
            credits_qs.values("status").annotate(count=Count("id")).values_list("status", "count")
        )

        schedules_qs = RepaymentSchedule.objects.filter(credit__in=credits_qs)
        total_due = schedules_qs.aggregate(total=Sum("amount_due"))["total"] or Decimal("0")
        total_paid = schedules_qs.aggregate(total=Sum("amount_paid"))["total"] or Decimal("0")
        recovery_rate = float((total_paid / total_due * 100) if total_due > 0 else 0)

        insurance_qs = InsuranceSubscription.objects.filter(status=InsuranceSubscription.Status.ACTIVE)
        if region:
            insurance_qs = insurance_qs.filter(client__region=region)

        open_conversations = Conversation.objects.filter(
            status__in=[Conversation.Status.OPEN, Conversation.Status.ASSIGNED]
        ).count()

        pending_credits = credits_qs.filter(
            status__in=[CreditApplication.Status.SUBMITTED, CreditApplication.Status.IN_REVIEW]
        ).count()

        return Response({
            "credits_by_status": credits_by_status,
            "total_credits": credits_qs.count(),
            "pending_credits": pending_credits,
            "recovery_rate_percent": round(recovery_rate, 2),
            "total_amount_due": str(total_due),
            "total_amount_paid": str(total_paid),
            "active_insurance_subscriptions": insurance_qs.count(),
            "open_support_conversations": open_conversations,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "agent": agent_id,
                "region": region,
            },
            "generated_at": timezone.now().isoformat(),
        })
