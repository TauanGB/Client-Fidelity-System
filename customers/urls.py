from django.urls import path

from .views import (
    CustomerCreateView,
    CustomerDetailView,
    CustomerListView,
    CustomerPublicLookupView,
    CustomerPublicProgressView,
    PurchaseAssociationView,
    CustomerUpdateView,
    register_purchase,
)


app_name = "customers"

urlpatterns = [
    path("", CustomerListView.as_view(), name="list"),
    path("new/", CustomerCreateView.as_view(), name="create"),
    path("purchases/new/", PurchaseAssociationView.as_view(), name="purchase-association"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", CustomerUpdateView.as_view(), name="update"),
    path("<int:customer_id>/purchase/", register_purchase, name="register-purchase"),
    path("progress/", CustomerPublicLookupView.as_view(), name="public-lookup"),
    path("progress/<int:pk>/", CustomerPublicProgressView.as_view(), name="public-progress"),
]
