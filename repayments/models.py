from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from credits.models import CreditApplication


class RepaymentSchedule(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        PAID = "paid", "Payé"
        LATE = "late", "En retard"
        PARTIAL = "partial", "Partiel"

    credit = models.ForeignKey(CreditApplication, on_delete=models.CASCADE, related_name="schedules")
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    alert_j3_sent = models.BooleanField(default=False)
    alert_j1_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["installment_number"]
        unique_together = ["credit", "installment_number"]

    def __str__(self):
        return f"Échéance {self.installment_number} - Crédit #{self.credit_id}"

    def update_status(self):
        today = timezone.now().date()
        if self.amount_paid >= self.amount_due + self.penalty_amount:
            self.status = self.Status.PAID
        elif self.amount_paid > 0:
            self.status = self.Status.PARTIAL
        elif today > self.due_date:
            self.status = self.Status.LATE
            days_late = (today - self.due_date).days
            rate = Decimal(str(settings.CREDIT_LATE_PENALTY_RATE))
            self.penalty_amount = (self.amount_due * rate * Decimal(days_late) / Decimal("30")).quantize(
                Decimal("0.01")
            )
        else:
            self.status = self.Status.PENDING
        self.save()


class Repayment(models.Model):
    schedule = models.ForeignKey(RepaymentSchedule, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, default="mobile_money")
    reference = models.CharField(max_length=100, blank=True)
    recorded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="recorded_repayments",
    )
    notes = models.TextField(blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at"]

    def __str__(self):
        return f"Paiement {self.amount} - Échéance #{self.schedule_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.schedule.amount_paid += self.amount
        self.schedule.save(update_fields=["amount_paid"])
        self.schedule.update_status()
