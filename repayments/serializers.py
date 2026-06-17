from rest_framework import serializers

from .models import Repayment, RepaymentSchedule


class RepaymentScheduleSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    credit_id = serializers.IntegerField(source="credit.id", read_only=True)

    class Meta:
        model = RepaymentSchedule
        fields = [
            "id",
            "credit_id",
            "installment_number",
            "due_date",
            "amount_due",
            "amount_paid",
            "penalty_amount",
            "status",
            "status_display",
        ]


class RepaymentSerializer(serializers.ModelSerializer):
    schedule_detail = RepaymentScheduleSerializer(source="schedule", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = Repayment
        fields = [
            "id",
            "schedule",
            "schedule_detail",
            "amount",
            "payment_method",
            "reference",
            "recorded_by",
            "recorded_by_name",
            "notes",
            "paid_at",
        ]
        read_only_fields = ["id", "recorded_by", "paid_at"]


class RepaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = ["schedule", "amount", "payment_method", "reference", "notes"]
