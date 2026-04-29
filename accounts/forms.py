from django import forms
from django.contrib.auth.forms import AuthenticationForm


class StoreAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Digite seu usuario",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Digite sua senha",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        "invalid_login": "Usuario ou senha invalidos. Verifique os dados e tente novamente.",
        "inactive": "Esta conta esta inativa.",
    }
