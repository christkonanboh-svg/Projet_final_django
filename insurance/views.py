from django.contrib.auth import get_user_model

from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAgentOrAdmin
from notifications.services import create_notification

from .models import InsuranceProduct, InsuranceSubscription, process_insurance_expiry_alerts
from .serializers import (
    InsuranceProductSerializer,
    InsuranceSubscribeSerializer,
    InsuranceSubscriptionSerializer,
)

User = get_user_model()


class InsuranceProductListView(generics.ListAPIView):
    queryset = InsuranceProduct.objects.filter(is_active=True)
    serializer_class = InsuranceProductSerializer
    permission_classes = [IsAuthenticated]


class InsuranceSubscriptionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InsuranceSubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        qs = InsuranceSubscription.objects.select_related("product", "client")
        if user.is_client:
            return qs.filter(client=user)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InsuranceSubscribeSerializer
        return InsuranceSubscriptionSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.is_client:
            return Response(
                {"detail": "Seuls les clients peuvent souscrire."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = InsuranceSubscribeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        create_notification(
            request.user,
            "Souscription confirmée",
            f"Votre police {subscription.policy_number} est active jusqu'au {subscription.end_date}.",
            "insurance_subscribed",
            {"subscription_id": subscription.id},
        )
        # Notify agents and admin
        staff = User.objects.filter(role__in=["agent", "admin"])
        for member in staff:
            create_notification(
                member,
                "Nouvelle souscription assurance",
                f"{request.user.get_full_name() or request.user.username} a souscrit à {subscription.product.name}.",
                "new_insurance_subscription",
                {"subscription_id": subscription.id, "client_id": request.user.id},
            )
        return Response(
            InsuranceSubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED,
        )


class ActivePoliciesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: InsuranceSubscriptionSerializer(many=True)})
    def get(self, request):
        qs = InsuranceSubscription.objects.filter(
            client=request.user,
            status=InsuranceSubscription.Status.ACTIVE,
        ).select_related("product")
        return Response(InsuranceSubscriptionSerializer(qs, many=True).data)


class ProcessInsuranceAlertsView(APIView):
    permission_classes = [IsAgentOrAdmin]
    serializer_class = None

    @extend_schema(
        request=None,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        process_insurance_expiry_alerts()
        return Response({"detail": "Alertes d'expiration assurance traitées."})
