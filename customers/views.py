from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView

from loyalty.forms import RewardRedemptionForm
from loyalty.models import LoyaltyCampaign
from loyalty.services import customer_progress

from .forms import CustomerForm, CustomerPublicLookupForm, PurchaseAssociationForm, PurchaseRecordForm
from .models import Customer, PurchaseRecord


def build_customer_month_status(customer, today=None):
    today = today or timezone.localdate()
    month_start = today.replace(day=1)
    last_purchase_at = getattr(customer, "last_purchase_at", None)
    if not last_purchase_at:
        return {
            "row_class": "customer-row-critical",
            "badge_class": "customer-status-critical",
            "label": "Sem compras",
            "detail": "Nenhuma compra registrada ainda.",
            "days_without_purchase": None,
            "has_purchased_this_month": False,
        }

    last_purchase_date = timezone.localtime(last_purchase_at).date()
    days_without_purchase = max((today - last_purchase_date).days, 0)
    has_purchased_this_month = last_purchase_date >= month_start
    if has_purchased_this_month:
        return {
            "row_class": "customer-row-fresh",
            "badge_class": "customer-status-fresh",
            "label": "Comprou neste mes",
            "detail": f"Ultima compra ha {days_without_purchase} dia(s).",
            "days_without_purchase": days_without_purchase,
            "has_purchased_this_month": True,
        }

    if days_without_purchase >= 30:
        row_class = "customer-row-critical"
        badge_class = "customer-status-critical"
        label = "Mais de 1 mes sem comprar"
    elif days_without_purchase >= 24:
        row_class = "customer-row-danger"
        badge_class = "customer-status-danger"
        label = "Muito perto de 1 mes"
    elif days_without_purchase >= 16:
        row_class = "customer-row-warning"
        badge_class = "customer-status-warning"
        label = "Atencao"
    else:
        row_class = "customer-row-watch"
        badge_class = "customer-status-watch"
        label = "Sem compra neste mes"

    return {
        "row_class": row_class,
        "badge_class": badge_class,
        "label": label,
        "detail": f"{days_without_purchase} dia(s) sem comprar.",
        "days_without_purchase": days_without_purchase,
        "has_purchased_this_month": False,
    }


class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = "customers/customer_list.html"
    context_object_name = "customers"

    def get_queryset(self):
        return Customer.objects.annotate(
            total_purchases=Count("purchase_records"),
            last_purchase_at=Max("purchase_records__created_at"),
        ).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        for customer in context["customers"]:
            customer.month_status = build_customer_month_status(customer, today=today)
        context["current_month_label"] = today.strftime("%m/%Y")
        return context


class PurchaseAssociationView(LoginRequiredMixin, FormView):
    template_name = "customers/purchase_association_form.html"
    form_class = PurchaseAssociationForm
    success_url = reverse_lazy("customers:purchase-association")
    search_limit = 12

    def get_selected_customer(self):
        customer_id = self.request.GET.get("customer")
        if self.request.method == "POST":
            customer_id = self.request.POST.get("customer")
        if customer_id:
            return Customer.objects.filter(pk=customer_id).first()
        return None

    def get_search_query(self):
        return (self.request.GET.get("q") or "").strip()

    def get_search_mode(self):
        return (self.request.GET.get("mode") or "all").strip().lower()

    def get_search_results(self, campaign):
        search_mode = self.get_search_mode()
        search_query = self.get_search_query()
        valid_modes = {"all", "phone", "name", "email", "recent", "almost-ready", "ready"}
        if search_mode not in valid_modes:
            search_mode = "all"

        queryset = Customer.objects.annotate(
            total_purchases=Count("purchase_records"),
            last_purchase_at=Max("purchase_records__created_at"),
        )
        should_search = bool(search_query) or search_mode in {"recent", "almost-ready", "ready"}
        if not should_search:
            return [], search_mode

        if search_mode == "recent":
            customers = list(queryset.order_by("-last_purchase_at", "-updated_at")[: self.search_limit])
        else:
            if search_mode == "phone":
                filtered = queryset.filter(phone__icontains=search_query)
            elif search_mode == "name":
                filtered = queryset.filter(name__icontains=search_query)
            elif search_mode == "email":
                filtered = queryset.filter(email__icontains=search_query)
            else:
                digits = "".join(char for char in search_query if char.isdigit())
                phone_query = Q()
                if digits:
                    phone_query = Q(phone__icontains=digits) | Q(phone__endswith=digits[-4:])
                filtered = queryset.filter(
                    Q(name__icontains=search_query)
                    | Q(email__icontains=search_query)
                    | phone_query
                )

            customers = list(filtered.order_by("name")[: self.search_limit])

        enriched_customers = []
        for customer in customers:
            progress = customer_progress(customer, campaign) if campaign else None
            if search_mode == "almost-ready" and (not progress or not progress.get("is_almost_ready")):
                continue
            if search_mode == "ready" and (not progress or not progress["is_eligible"]):
                continue
            customer.progress_snapshot = progress
            enriched_customers.append(customer)

        if search_mode in {"almost-ready", "ready"}:
            if search_mode == "almost-ready":
                enriched_customers.sort(
                    key=lambda customer: (
                        customer.progress_snapshot["remaining_purchases"],
                        -(customer.progress_snapshot["purchase_count"]),
                        customer.name.lower(),
                    )
                )
            else:
                enriched_customers.sort(
                    key=lambda customer: (
                        not customer.progress_snapshot["is_eligible"],
                        customer.name.lower(),
                    )
                )
            enriched_customers = enriched_customers[: self.search_limit]

        return enriched_customers, search_mode

    def get_initial(self):
        initial = super().get_initial()
        selected_customer = self.get_selected_customer()
        if selected_customer:
            initial["customer"] = selected_customer.pk
        return initial

    def form_valid(self, form):
        campaign = LoyaltyCampaign.get_active()
        if not campaign:
            messages.error(self.request, "Cadastre uma campanha antes de associar compras.")
            return self.form_invalid(form)

        customer = form.cleaned_data["customer"]
        PurchaseRecord.objects.create(
            customer=customer,
            campaign=campaign,
            notes=form.cleaned_data["notes"],
        )
        messages.success(self.request, f"Compra associada com sucesso para {customer.name}.")
        self.success_url = reverse_lazy("customers:detail", kwargs={"pk": customer.pk})
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = LoyaltyCampaign.get_active()
        selected_customer = self.get_selected_customer()
        search_results, search_mode = self.get_search_results(campaign)

        context["campaign"] = campaign
        context["search_query"] = self.get_search_query()
        context["search_mode"] = search_mode
        context["search_results"] = search_results
        context["selected_customer"] = selected_customer
        context["selected_customer_progress"] = customer_progress(selected_customer, campaign) if selected_customer and campaign else None
        context["selected_customer_last_purchase"] = (
            selected_customer.purchase_records.order_by("-created_at").first() if selected_customer else None
        )
        context["recent_purchases"] = PurchaseRecord.objects.select_related("customer", "campaign")[:8]
        return context


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"
    success_url = reverse_lazy("customers:list")

    def form_valid(self, form):
        messages.success(self.request, "Cliente cadastrado com sucesso.")
        return super().form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"

    def get_success_url(self):
        return reverse_lazy("customers:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Cliente atualizado com sucesso.")
        return super().form_valid(form)


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = "customers/customer_detail.html"
    context_object_name = "customer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object
        campaign = LoyaltyCampaign.get_active()
        context["campaign"] = campaign
        context["progress"] = customer_progress(customer, campaign)
        context["purchase_form"] = PurchaseRecordForm()
        context["redemption_form"] = RewardRedemptionForm()
        context["purchase_records"] = customer.purchase_records.select_related("campaign")[:10]
        context["redemptions"] = customer.reward_redemptions.select_related("campaign")[:10]
        return context


@login_required
def register_purchase(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    campaign = LoyaltyCampaign.get_active()
    if request.method != "POST":
        return redirect("customers:detail", pk=customer.pk)
    if not campaign:
        messages.error(request, "Cadastre uma campanha antes de registrar compras.")
        return redirect("customers:detail", pk=customer.pk)

    form = PurchaseRecordForm(request.POST)
    if form.is_valid():
        purchase = form.save(commit=False)
        purchase.customer = customer
        purchase.campaign = campaign
        purchase.save()
        messages.success(request, "Compra registrada com sucesso.")
    else:
        messages.error(request, "Não foi possível registrar a compra.")
    return redirect("customers:detail", pk=customer.pk)


class CustomerPublicLookupView(View):
    template_name = "customers/public_lookup.html"

    def get(self, request):
        form = CustomerPublicLookupForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CustomerPublicLookupForm(request.POST)
        customers = None
        if form.is_valid():
            phone = form.cleaned_data["phone"].strip()
            customers = Customer.objects.filter(phone__icontains=phone).order_by("name")
            if customers.count() == 1:
                return redirect("customers:public-progress", pk=customers.first().pk)
            if not customers.exists():
                messages.error(request, "Nenhum cliente encontrado com esse telefone.")
        return render(request, self.template_name, {"form": form, "customers": customers})


class CustomerPublicProgressView(TemplateView):
    template_name = "customers/public_progress.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = get_object_or_404(Customer, pk=self.kwargs["pk"])
        progress = customer_progress(customer)
        context["customer"] = customer
        context["progress"] = progress
        return context
