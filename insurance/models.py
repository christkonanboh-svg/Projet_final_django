from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class InsuranceProduct(models.Model):
    class ProductType(models.TextChoices):
        LIFE = "life", "Assurance vie"
        DEATH_DISABILITY = "death_disability", "Décès-Invalidité"

    name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=30, choices=ProductType.choices)
    description = models.TextField()
    premium_amount = models.DecimalField(max_digits=12, decimal_places=2)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration_months = models.PositiveIntegerField(default=12)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InsuranceSubscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expirée"
        CANCELLED = "cancelled", "Annulée"

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="insurance_subscriptions")
    product = models.ForeignKey(InsuranceProduct, on_delete=models.PROTECT, related_name="subscriptions")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    premium_paid = models.DecimalField(max_digits=12, decimal_places=2)
    policy_number = models.CharField(max_length=50, unique=True)
    expiry_alert_sent = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return f"{self.policy_number} - {self.client.username}"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE and self.end_date >= timezone.now().date()


def process_insurance_expiry_alerts():
    from notifications.services import create_notification

    alert_date = timezone.now().date() + timezone.timedelta(days=settings.INSURANCE_EXPIRY_ALERT_DAYS)
    subscriptions = InsuranceSubscription.objects.filter(
        status=InsuranceSubscription.Status.ACTIVE,
        end_date=alert_date,
        expiry_alert_sent=False,
    ).select_related("client", "product")

    for sub in subscriptions:
        create_notification(
            sub.client,
            "Expiration assurance proche",
            f"Votre police {sub.policy_number} ({sub.product.name}) expire le {sub.end_date}.",
            "insurance_expiry",
            {"subscription_id": sub.id, "policy_number": sub.policy_number},
        )
        sub.expiry_alert_sent = True
        sub.save(update_fields=["expiry_alert_sent"])
