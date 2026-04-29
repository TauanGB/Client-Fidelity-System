from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

from .forms import StoreAuthenticationForm


class StoreLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    authentication_form = StoreAuthenticationForm


def store_logout_view(request):
    logout(request)
    return redirect("accounts:login")
