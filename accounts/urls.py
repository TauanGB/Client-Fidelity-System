from django.urls import path

from .views import StoreLoginView, store_logout_view


app_name = "accounts"

urlpatterns = [
    path("login/", StoreLoginView.as_view(), name="login"),
    path("logout/", store_logout_view, name="logout"),
]
