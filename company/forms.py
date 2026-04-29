from django import forms

from core.form_widgets import StyledClearableFileInput
from core.image_specs import IMAGE_REQUIREMENTS, validate_image_requirements

from .models import CompanySettings


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
            "name": forms.TextInput(attrs={"placeholder": "Nome da loja ou empresa"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Como sua empresa quer ser apresentada?"}),
            "phone": forms.TextInput(attrs={"placeholder": "(00) 0000-0000"}),
            "address": forms.TextInput(attrs={"placeholder": "Endereco da unidade"}),
            "instagram": forms.TextInput(attrs={"placeholder": "@sualoja"}),
            "whatsapp": forms.TextInput(attrs={"placeholder": "(00) 00000-0000"}),
            "theme": forms.RadioSelect(),
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Nome da empresa"
        self.fields["description"].label = "Descricao da empresa"
        self.fields["description"].help_text = "Esse texto pode aparecer nas superficies publicas da loja."
        self.fields["phone"].label = "Telefone principal"
        self.fields["address"].label = "Endereco"
        self.fields["instagram"].label = "Instagram"
        self.fields["instagram"].help_text = "Informe o usuario principal da loja."
        self.fields["whatsapp"].label = "WhatsApp"
        self.fields["theme"].label = "Tema visual"
        self.fields["theme"].choices = [
            ("classic", "Classico"),
            ("sunset", "Por do sol"),
            ("forest", "Floresta"),
        ]
        self.fields["primary_color"].label = "Cor principal"
        self.fields["secondary_color"].label = "Cor secundaria"
        self.fields["logo"].label = "Logo"
        self.fields["banner"].label = "Banner"

    def clean_logo(self):
        return validate_image_requirements(self.cleaned_data.get("logo"), "company_logo")

    def clean_banner(self):
        return validate_image_requirements(self.cleaned_data.get("banner"), "company_banner")
