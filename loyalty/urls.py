from django.urls import path

from .views import LoyaltyCampaignUpdateView, redeem_reward


app_name = "loyalty"

urlpatterns = [
    path("campaign/", LoyaltyCampaignUpdateView.as_view(), name="campaign-settings"),
    path("customers/<int:customer_id>/redeem/", redeem_reward, name="redeem-reward"),
]
