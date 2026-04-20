from django.contrib import admin

from .models import LoyaltyCampaign, RewardRedemption, ThemePreset


@admin.register(LoyaltyCampaign)
class LoyaltyCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "required_purchases", "reward_name", "is_active", "updated_at")


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ("customer", "campaign", "redeemed_at")
    list_filter = ("campaign",)


@admin.register(ThemePreset)
class ThemePresetAdmin(admin.ModelAdmin):
    list_display = ("name", "css_class", "is_active")
