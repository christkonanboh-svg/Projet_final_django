import uuid
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import serializers

from .models import InsuranceProduct, InsuranceSubscription


class InsuranceProductSerializer(serializers.ModelSerializer):
    product_type_display = serializers.CharField(source="get_product_type_display", read_only=True)

    class Meta:
        model = InsuranceProduct
        fields = [
            "id",
            "name",
            "product_type",
            "product_type_display",
            "description",
            "premium_amount",
            "coverage_amount",
            "duration_months",
            "is_active",
        ]


class InsuranceSubscriptionSerializer(serializers.ModelSerializer):
    product_detail = InsuranceProductSerializer(source="product", read_only=True)
    client_name = serializers.CharField(source="client.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    is_active_policy = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = InsuranceSubscription
        fields = [
            "id",
            "client",
            "client_name",
            "product",
            "product_detail",
            "start_date",
            "end_date",
            "status",
            "status_display",
            "is_active_policy",
            "premium_paid",
            "policy_number",
            "subscribed_at",
        ]
        read_only_fields = [
            "id",
            "client",
            "start_date",
            "end_date",
            "status",
            "premium_paid",
            "policy_number",
            "subscribed_at",
        ]


class InsuranceSubscribeSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=InsuranceProduct.objects.filter(is_active=True),
        source="product",
    )

    def create(self, validated_data):
        user = self.context["request"].user
        product = validated_data["product"]
        start_date = timezone.now().date()
        end_date = start_date + relativedelta(months=product.duration_months)
        policy_number = f"POL-{uuid.uuid4().hex[:8].upper()}"
        return InsuranceSubscription.objects.create(
            client=user,
            product=product,
            start_date=start_date,
            end_date=end_date,
            premium_paid=product.premium_amount,
            policy_number=policy_number,
        )
