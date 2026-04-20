from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import UpdateView

from core.image_specs import IMAGE_REQUIREMENTS
from customers.models import Customer

from .forms import LoyaltyCampaignForm, RewardRedemptionForm
from .models import LoyaltyCampaign
from .services import customer_progress


class LoyaltyCampaignUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "loyalty/campaign_form.html"
    form_class = LoyaltyCampaignForm
    success_url = "/loyalty/campaign/"

    def get_object(self, queryset=None):
        campaign = LoyaltyCampaign.get_active()
        if campaign:
            return campaign
        return LoyaltyCampaign(is_active=True)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Campanha salva com sucesso.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reward_image_requirement"] = IMAGE_REQUIREMENTS["reward_image"]
        return context


@login_required
def redeem_reward(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    campaign = LoyaltyCampaign.get_active()
    if not campaign:
        messages.error(request, "Cadastre uma campanha antes de registrar resgates.")
        return redirect("customers:detail", pk=customer.pk)

    progress = customer_progress(customer, campaign)
    if request.method != "POST":
        return redirect("customers:detail", pk=customer.pk)

    form = RewardRedemptionForm(request.POST)
    if not progress["is_eligible"]:
        messages.error(request, "O cliente ainda não atingiu a meta da campanha.")
    elif form.is_valid():
        redemption = form.save(commit=False)
        redemption.customer = customer
        redemption.campaign = campaign
        redemption.save()
        messages.success(request, "Resgate registrado e ciclo reiniciado.")
    else:
        messages.error(request, "Não foi possível registrar o resgate.")
    return redirect("customers:detail", pk=customer.pk)
