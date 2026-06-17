from django.contrib import admin

from .models import InsuranceProduct, InsuranceSubscription


@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):
    list_display = ("name", "product_type", "premium_amount", "is_active")


@admin.register(InsuranceSubscription)
class InsuranceSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("policy_number", "client", "product", "status", "end_date")
