from django.urls import path

from .portfolio_views import PortfolioView
from .views import DashboardView


app_name = "core"

urlpatterns = [
    path("", PortfolioView.as_view(), name="home"),
    path("styles.css", PortfolioView.as_view(asset="styles.css"), name="portfolio-styles"),
    path("app.js", PortfolioView.as_view(asset="app.js"), name="portfolio-script"),
    path("favicon.svg", PortfolioView.as_view(asset="favicon.svg"), name="portfolio-favicon"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
