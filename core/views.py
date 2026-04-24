from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from .flow import build_panel_flow
from company.models import CompanySettings
from customers.models import Customer, PurchaseRecord
from loyalty.models import LoyaltyCampaign, RewardRedemption


class HomeRedirectView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:dashboard")
        return redirect("accounts:login")


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
