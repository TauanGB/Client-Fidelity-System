from django.urls import path

from .views import CompanySettingsUpdateView


app_name = "company"

urlpatterns = [
    path("settings/", CompanySettingsUpdateView.as_view(), name="settings"),
]
