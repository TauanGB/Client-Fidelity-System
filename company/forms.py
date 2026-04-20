from django import forms

from core.image_specs import IMAGE_REQUIREMENTS, validate_image_requirements

from .models import CompanySettings


class StyledClearableFileInput(forms.ClearableFileInput):
    template_name = "widgets/clearable_image_input.html"


class CompanySettingsForm(forms.ModelForm):
    logo = forms.FileField(
        required=False,
        help_text=IMAGE_REQUIREMENTS["company_logo"].help_text,
        widget=StyledClearableFileInput(attrs={"accept": ".png,.jpg,.jpeg,.webp"}),
    )
    banner = forms.FileField(
        required=False,
        help_text=IMAGE_REQUIREMENTS["company_banner"].help_text,
        widget=StyledClearableFileInput(attrs={"accept": ".png,.jpg,.jpeg,.webp"}),
    )

    class Meta:
        model = CompanySettings
        fields = [
            "name",
            "description",
            "phone",
            "address",
            "instagram",
            "whatsapp",
            "theme",
            "primary_color",
            "secondary_color",
            "logo",
            "banner",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "theme": forms.RadioSelect(),
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
        }

    def clean_logo(self):
        return validate_image_requirements(self.cleaned_data.get("logo"), "company_logo")

    def clean_banner(self):
        return validate_image_requirements(self.cleaned_data.get("banner"), "company_banner")
