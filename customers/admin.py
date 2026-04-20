from django.contrib import admin

from .models import Customer, PurchaseRecord


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "created_at")
    search_fields = ("name", "phone", "email")


@admin.register(PurchaseRecord)
class PurchaseRecordAdmin(admin.ModelAdmin):
    list_display = ("customer", "campaign", "created_at")
    list_filter = ("campaign",)
