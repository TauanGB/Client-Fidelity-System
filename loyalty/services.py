from customers.models import PurchaseRecord

from .models import LoyaltyCampaign, RewardRedemption


def last_redemption(customer, campaign):
    return (
        RewardRedemption.objects.filter(customer=customer, campaign=campaign)
        .order_by("-redeemed_at")
        .first()
    )


def purchases_in_current_cycle(customer, campaign):
    queryset = PurchaseRecord.objects.filter(customer=customer, campaign=campaign)
    previous_redemption = last_redemption(customer, campaign)
    if previous_redemption:
        queryset = queryset.filter(created_at__gt=previous_redemption.redeemed_at)
    return queryset.order_by("-created_at")


def customer_progress(customer, campaign=None):
    campaign = campaign or LoyaltyCampaign.get_active()
    if not campaign:
        return {
            "campaign": None,
            "purchase_count": 0,
            "required_purchases": 0,
            "remaining_purchases": 0,
            "is_eligible": False,
            "progress_percent": 0,
        }

    purchase_count = purchases_in_current_cycle(customer, campaign).count()
    required = campaign.required_purchases
    remaining = max(required - purchase_count, 0)
    is_eligible = purchase_count >= required
    progress_percent = min(int((purchase_count / required) * 100), 100) if required else 0
    return {
        "campaign": campaign,
        "purchase_count": purchase_count,
        "required_purchases": required,
        "remaining_purchases": remaining,
        "is_eligible": is_eligible,
        "progress_percent": progress_percent,
    }
