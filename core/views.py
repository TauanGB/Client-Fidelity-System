from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .flow import build_panel_flow
from company.models import CompanySettings
from customers.models import Customer, PurchaseRecord
from loyalty.models import LoyaltyCampaign, RewardRedemption


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = CompanySettings.get_solo()
        campaign = LoyaltyCampaign.get_active()
        customer_count = Customer.objects.count()
        context["company"] = company
        context["campaign"] = campaign
        context["customer_count"] = customer_count
        context["purchase_count"] = PurchaseRecord.objects.count()
        context["redemption_count"] = RewardRedemption.objects.count()
        context["latest_customers"] = Customer.objects.order_by("-created_at")[:5]
        context["panel_flow"] = build_panel_flow(
            company=company,
            campaign=campaign,
            has_customers=customer_count > 0,
        )
        return context
