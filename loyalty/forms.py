from django import forms

from core.form_widgets import StyledClearableFileInput
from core.image_specs import IMAGE_REQUIREMENTS, validate_image_requirements

from .models import LoyaltyCampaign, RewardRedemption


class LoyaltyCampaignForm(forms.ModelForm):
    reward_image = forms.FileField(
        required=False,
        help_text=IMAGE_REQUIREMENTS["reward_image"].help_text,
        widget=StyledClearableFileInput(attrs={"accept": ".png,.jpg,.jpeg,.webp"}),
    )

    class Meta:
        model = LoyaltyCampaign
        fields = [
            "name",
            "description",
            "rule_type",
            "required_purchases",
            "cycle_length_months",
            "minimum_purchases_per_month",
            "reward_name",
            "reward_description",
            "reward_image",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nome interno da campanha"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Explique a campanha em linguagem simples"}),
            "reward_description": forms.Textarea(attrs={"rows": 4, "placeholder": "Detalhes do premio e regras de uso"}),
            "cycle_length_months": forms.NumberInput(attrs={"min": 1, "placeholder": "3"}),
            "minimum_purchases_per_month": forms.NumberInput(attrs={"min": 1, "placeholder": "2"}),
            "required_purchases": forms.NumberInput(attrs={"min": 1, "placeholder": "10"}),
            "reward_name": forms.TextInput(attrs={"placeholder": "Ex.: Banho gratis"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Nome da campanha"
        self.fields["description"].label = "Descricao da campanha"
        self.fields["rule_type"].label = "Tipo de regra"
        self.fields["rule_type"].help_text = "Escolha se a campanha funciona por total de compras ou por meses consecutivos."
        self.fields["required_purchases"].label = "Compras para liberar o premio"
        self.fields["required_purchases"].help_text = "Usado apenas na regra tradicional por total de compras."
        self.fields["cycle_length_months"].label = "Meses consecutivos do ciclo"
        self.fields["cycle_length_months"].help_text = "Quantidade de meses consecutivos que completam o ciclo."
        self.fields["minimum_purchases_per_month"].label = "Compras minimas por mes"
        self.fields["minimum_purchases_per_month"].help_text = "Quantidade minima de compras exigida em cada mes do ciclo."
        self.fields["reward_name"].label = "Nome do premio"
        self.fields["reward_description"].label = "Descricao do premio"
        self.fields["reward_image"].label = "Imagem do premio"
        self.fields["is_active"].label = "Campanha ativa"
        self.fields["is_active"].help_text = "Ao ativar esta campanha, as demais campanhas ficam inativas."

    def clean_reward_image(self):
        return validate_image_requirements(self.cleaned_data.get("reward_image"), "reward_image")


class RewardRedemptionForm(forms.ModelForm):
    class Meta:
        model = RewardRedemption
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Observacoes sobre o resgate realizado",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].label = "Observacoes do resgate"
        self.fields["notes"].required = False
        self.fields["notes"].help_text = "Campo opcional para registrar detalhes internos do resgate."
