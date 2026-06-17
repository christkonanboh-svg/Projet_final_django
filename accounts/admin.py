from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "region", "is_online", "is_staff")
    list_filter = ("role", "region", "is_online")
    fieldsets = UserAdmin.fieldsets + (
        ("COFINANCE", {"fields": ("role", "phone", "region", "is_online")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("COFINANCE", {"fields": ("role", "phone", "region")}),
    )
