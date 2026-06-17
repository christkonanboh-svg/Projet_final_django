from django.conf import settings
from django.utils import timezone

from notifications.services import create_notification


def process_repayment_alerts():
    """Génère les alertes J-3 et J+1 pour les échéances."""
    from .models import RepaymentSchedule

    today = timezone.now().date()
    j3 = today + timezone.timedelta(days=settings.REPAYMENT_ALERT_DAYS_BEFORE)
    j1_past = today - timezone.timedelta(days=settings.REPAYMENT_ALERT_DAYS_AFTER)

    for schedule in RepaymentSchedule.objects.filter(
        status__in=[RepaymentSchedule.Status.PENDING, RepaymentSchedule.Status.LATE],
        due_date=j3,
        alert_j3_sent=False,
    ).select_related("credit__client"):
        create_notification(
            schedule.credit.client,
            "Échéance à venir",
            f"Votre échéance n°{schedule.installment_number} arrive dans 3 jours "
            f"({schedule.amount_due} FCFA).",
            "repayment_reminder_j3",
            {"schedule_id": schedule.id, "credit_id": schedule.credit_id},
        )
        schedule.alert_j3_sent = True
        schedule.save(update_fields=["alert_j3_sent"])

    for schedule in RepaymentSchedule.objects.filter(
        status=RepaymentSchedule.Status.LATE,
        due_date=j1_past,
        alert_j1_sent=False,
    ).select_related("credit__client"):
        create_notification(
            schedule.credit.client,
            "Échéance en retard",
            f"Votre échéance n°{schedule.installment_number} est en retard. "
            f"Pénalité : {schedule.penalty_amount} FCFA.",
            "repayment_late_j1",
            {"schedule_id": schedule.id, "credit_id": schedule.credit_id},
        )
        schedule.alert_j1_sent = True
        schedule.save(update_fields=["alert_j1_sent"])
