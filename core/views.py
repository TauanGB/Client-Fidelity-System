from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

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
        context["company"] = CompanySettings.get_solo()
        context["campaign"] = LoyaltyCampaign.get_active()
        context["customer_count"] = Customer.objects.count()
        context["purchase_count"] = PurchaseRecord.objects.count()
        context["redemption_count"] = RewardRedemption.objects.count()
        context["latest_customers"] = Customer.objects.order_by("-created_at")[:5]
        return context
