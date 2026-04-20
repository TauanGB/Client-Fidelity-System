from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

from core.image_specs import IMAGE_REQUIREMENTS

from .forms import CompanySettingsForm
from .models import CompanySettings


class CompanySettingsUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "company/settings_form.html"
    form_class = CompanySettingsForm
    success_url = "/company/settings/"

    def get_object(self, queryset=None):
        company = CompanySettings.get_solo()
        if company:
            return company
        return CompanySettings()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Configurações da empresa salvas.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Corrija os campos destacados.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_requirements"] = {
            "logo": IMAGE_REQUIREMENTS["company_logo"],
            "banner": IMAGE_REQUIREMENTS["company_banner"],
        }
        return context
