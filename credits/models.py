from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class CreditApplication(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Soumise"
        IN_REVIEW = "in_review", "En analyse"
        APPROVED = "approved", "Approuvée"
        DISBURSED = "disbursed", "Décaissée"
        REJECTED = "rejected", "Rejetée"

    class Frequency(models.TextChoices):
        WEEKLY = "weekly", "Hebdomadaire"
        MONTHLY = "monthly", "Mensuel"

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credit_applications")
    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_credits",
        limit_choices_to={"role__in": [User.Role.AGENT, User.Role.ADMIN]},
    )
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField()
    duration_months = models.PositiveIntegerField(default=6)
    repayment_frequency = models.CharField(
        max_length=20, choices=Frequency.choices, default=Frequency.MONTHLY
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    eligibility_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    interest_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.1200"))
    region = models.CharField(max_length=30, choices=User.Region.choices, blank=True)
    rejection_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Crédit #{self.pk} - {self.client.username} ({self.get_status_display()})"


class CreditDocument(models.Model):
    credit = models.ForeignKey(CreditApplication, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to="credit_documents/")
    document_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} - Crédit #{self.credit_id}"


def calculate_eligibility_score(client, amount_requested):
    """Score simplifié basé sur l'historique client."""
    base_score = Decimal("50.00")
    approved_count = CreditApplication.objects.filter(
        client=client, status=CreditApplication.Status.DISBURSED
    ).count()
    base_score += Decimal(approved_count * 10)

    if amount_requested <= Decimal("500000"):
        base_score += Decimal("15.00")
    elif amount_requested <= Decimal("1000000"):
        base_score += Decimal("10.00")

    if client.phone:
        base_score += Decimal("5.00")
    if client.region:
        base_score += Decimal("5.00")

    return min(base_score, Decimal("100.00"))


def generate_repayment_schedule(credit):
    from repayments.models import RepaymentSchedule

    principal = credit.amount_requested
    rate = credit.interest_rate
    months = credit.duration_months
    total_interest = principal * rate * Decimal(months) / Decimal("12")
    total_amount = principal + total_interest

    if credit.repayment_frequency == CreditApplication.Frequency.WEEKLY:
        installments = months * 4
    else:
        installments = months

    installment_amount = (total_amount / Decimal(installments)).quantize(Decimal("0.01"))
    start_date = timezone.now().date()

    if credit.repayment_frequency == CreditApplication.Frequency.WEEKLY:
        delta_days = 7
    else:
        delta_days = 30

    schedules = []
    for i in range(1, installments + 1):
        due_date = start_date + timedelta(days=delta_days * i)
        schedules.append(
            RepaymentSchedule(
                credit=credit,
                installment_number=i,
                due_date=due_date,
                amount_due=installment_amount,
            )
        )
    RepaymentSchedule.objects.bulk_create(schedules)
    return schedules
