from django.contrib import admin

from .models import Repayment, RepaymentSchedule


@admin.register(RepaymentSchedule)
class RepaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ("credit", "installment_number", "due_date", "amount_due", "status")


@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ("schedule", "amount", "recorded_by", "paid_at")
