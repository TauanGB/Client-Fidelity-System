from django.urls import reverse

from company.models import CompanySettings
from customers.models import Customer
from loyalty.models import LoyaltyCampaign


def build_panel_flow(company=None, campaign=None, has_customers=None):
    company = company if company is not None else CompanySettings.get_solo()
    campaign = campaign if campaign is not None else LoyaltyCampaign.get_active()
    has_customers = Customer.objects.exists() if has_customers is None else has_customers

    company_ready = bool(company and company.name)
    campaign_ready = bool(campaign and campaign.name)
    setup_ready = company_ready and campaign_ready

    required_steps = [
        {
            "key": "company",
            "title": "Configurar empresa",
            "description": "Defina nome, identidade visual e contatos que aparecem no sistema.",
            "href": reverse("company:settings"),
            "cta": "Abrir empresa",
            "is_complete": company_ready,
            "is_required": True,
        },
        {
            "key": "campaign",
            "title": "Configurar campanha",
            "description": "Defina quantas compras liberam o prêmio e como a campanha será apresentada.",
            "href": reverse("loyalty:campaign-settings"),
            "cta": "Abrir campanha",
            "is_complete": campaign_ready,
            "is_required": True,
        },
    ]

    recommended_steps = [
        {
            "key": "first-customer",
            "title": "Cadastrar primeiro cliente",
            "description": "Crie um primeiro cadastro para começar a operação e testar o fluxo completo.",
            "href": reverse("customers:create"),
            "cta": "Novo cliente",
            "is_complete": has_customers,
            "is_required": False,
        }
    ]

    if not company_ready:
        next_action = {
            "title": "Começar pela empresa",
            "description": "O primeiro passo é personalizar a instância com os dados e a identidade da loja.",
            "href": reverse("company:settings"),
            "cta": "Configurar empresa",
        }
    elif not campaign_ready:
        next_action = {
            "title": "Definir a campanha",
            "description": "Com a empresa pronta, falta cadastrar a regra de fidelidade que será usada no balcão.",
            "href": reverse("loyalty:campaign-settings"),
            "cta": "Configurar campanha",
        }
    elif not has_customers:
        next_action = {
            "title": "Cadastrar o primeiro cliente",
            "description": "A estrutura principal já está pronta. Agora vale registrar o primeiro cliente para iniciar a operação.",
            "href": reverse("customers:create"),
            "cta": "Cadastrar cliente",
        }
    else:
        next_action = {
            "title": "Sistema pronto para operação",
            "description": "Daqui em diante, o uso principal será cadastrar clientes novos e registrar compras do dia.",
            "href": reverse("customers:purchase-association"),
            "cta": "Registrar compra",
        }

    required_completed = sum(step["is_complete"] for step in required_steps)
    return {
        "company_ready": company_ready,
        "campaign_ready": campaign_ready,
        "setup_ready": setup_ready,
        "has_customers": has_customers,
        "required_steps": required_steps,
        "recommended_steps": recommended_steps,
        "required_completed": required_completed,
        "required_total": len(required_steps),
        "next_action": next_action,
    }
