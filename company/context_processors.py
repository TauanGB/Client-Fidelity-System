from .models import CompanySettings


def company_branding(request):
    company = CompanySettings.get_solo()
    return {
        "company_settings": company,
    }
