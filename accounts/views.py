from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect


class StoreLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def store_logout_view(request):
    logout(request)
    return redirect("accounts:login")
