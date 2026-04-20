from django import forms

from .models import Customer, PurchaseRecord


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email"]


class PurchaseRecordForm(forms.ModelForm):
    class Meta:
        model = PurchaseRecord
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Observações da compra"}),
        }


class CustomerPublicLookupForm(forms.Form):
    phone = forms.CharField(label="Telefone", max_length=20)


class PurchaseAssociationForm(forms.Form):
    customer = forms.ModelChoiceField(
        label="Cliente",
        queryset=Customer.objects.none(),
        widget=forms.HiddenInput(),
    )
    notes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Detalhes opcionais da compra"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.order_by("name")
