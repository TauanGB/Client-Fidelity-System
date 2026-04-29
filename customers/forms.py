from django import forms

from .models import Customer, PurchaseRecord


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "pet_count"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nome do cliente"}),
            "phone": forms.TextInput(attrs={"placeholder": "(00) 00000-0000"}),
            "email": forms.EmailInput(attrs={"placeholder": "cliente@exemplo.com"}),
            "pet_count": forms.NumberInput(attrs={"min": 1, "placeholder": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Nome completo"
        self.fields["phone"].label = "Telefone"
        self.fields["email"].label = "E-mail"
        self.fields["pet_count"].label = "Quantidade de pets"
        self.fields["pet_count"].help_text = "Informe quantos pets esse cliente possui."


class PurchaseRecordForm(forms.ModelForm):
    class Meta:
        model = PurchaseRecord
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Observacoes da compra, atendimento ou pedido",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].label = "Observacoes da compra"
        self.fields["notes"].required = False
        self.fields["notes"].help_text = "Campo opcional para registrar detalhes internos."


class CustomerPublicLookupForm(forms.Form):
    phone = forms.CharField(
        label="Telefone",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "Digite seu telefone"}),
    )


class PurchaseAssociationForm(forms.Form):
    customer = forms.ModelChoiceField(
        label="Cliente",
        queryset=Customer.objects.none(),
        widget=forms.HiddenInput(),
    )
    notes = forms.CharField(
        label="Observacoes da compra",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Detalhes opcionais da compra",
            }
        ),
        help_text="Campo opcional para contextualizar a compra no historico do cliente.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.order_by("name")
