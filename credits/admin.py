from django.contrib import admin

from .models import CreditApplication, CreditDocument


class CreditDocumentInline(admin.TabularInline):
    model = CreditDocument
    extra = 0


@admin.register(CreditApplication)
class CreditApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "amount_requested", "status", "eligibility_score", "submitted_at")
    list_filter = ("status", "region", "repayment_frequency")
    inlines = [CreditDocumentInline]
