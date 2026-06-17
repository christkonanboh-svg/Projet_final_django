from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CreditApplication, CreditDocument

User = get_user_model()


class CreditDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditDocument
        fields = ["id", "file", "document_type", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class CreditApplicationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    documents = CreditDocumentSerializer(many=True, read_only=True)
    assigned_agent_name = serializers.CharField(
        source="assigned_agent.get_full_name", read_only=True, default=None
    )

    class Meta:
        model = CreditApplication
        fields = [
            "id",
            "client",
            "client_name",
            "assigned_agent",
            "assigned_agent_name",
            "amount_requested",
            "purpose",
            "duration_months",
            "repayment_frequency",
            "status",
            "status_display",
            "eligibility_score",
            "interest_rate",
            "region",
            "rejection_reason",
            "documents",
            "submitted_at",
            "updated_at",
            "approved_at",
            "disbursed_at",
        ]
        read_only_fields = [
            "id",
            "client",
            "status",
            "eligibility_score",
            "interest_rate",
            "submitted_at",
            "updated_at",
            "approved_at",
            "disbursed_at",
        ]


class CreditCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditApplication
        fields = [
            "amount_requested",
            "purpose",
            "duration_months",
            "repayment_frequency",
            "region",
        ]


class CreditStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CreditApplication.Status.choices)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    assigned_agent = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=[User.Role.AGENT, User.Role.ADMIN]),
        required=False,
        allow_null=True,
    )


class CreditDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditDocument
        fields = ["file", "document_type"]
