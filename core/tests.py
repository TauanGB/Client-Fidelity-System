from datetime import date, datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from company.models import CompanySettings
from customers.models import Customer, PurchaseRecord
from loyalty.models import LoyaltyCampaign, RewardRedemption
from loyalty.services import customer_progress


class MvpFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="lojista", password="senha-segura-123")
        self.company = CompanySettings.objects.create(name="Loja Exemplo")
        self.campaign = LoyaltyCampaign.objects.create(
            name="Cartao Fidelidade",
            required_purchases=3,
            reward_name="Cafe gratis",
            is_active=True,
        )
        self.customer = Customer.objects.create(
            name="Maria",
            phone="11999999999",
            email="maria@example.com",
            pet_count=2,
        )
        self.customer_two = Customer.objects.create(
            name="Marcos",
            phone="11888887777",
            email="marcos@example.com",
            pet_count=1,
        )

    def aware_datetime(self, year, month, day, hour=10, minute=0):
        return timezone.make_aware(datetime(year, month, day, hour, minute))

    def create_purchase(self, customer, when, campaign=None, notes=""):
        purchase = PurchaseRecord.objects.create(
            customer=customer,
            campaign=campaign or self.campaign,
            notes=notes,
        )
        PurchaseRecord.objects.filter(pk=purchase.pk).update(created_at=when)
        purchase.refresh_from_db()
        return purchase

    def create_redemption(self, customer, when, campaign=None, notes=""):
        redemption = RewardRedemption.objects.create(
            customer=customer,
            campaign=campaign or self.campaign,
            notes=notes,
        )
        RewardRedemption.objects.filter(pk=redemption.pk).update(redeemed_at=when)
        redemption.refresh_from_db()
        return redemption

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_dashboard_prioritizes_operation_when_setup_is_ready(self):
        self.client.login(username="lojista", password="senha-segura-123")
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Central de operacao")
        self.assertContains(response, "Registrar compra")
        self.assertContains(response, "Novo cliente")

    def test_dashboard_guides_initial_setup_when_campaign_is_missing(self):
        self.campaign.delete()
        self.client.login(username="lojista", password="senha-segura-123")
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Configuracao inicial")
        self.assertContains(response, "Configurar campanha")

    def test_purchase_progress_and_redemption_cycle(self):
        for _ in range(3):
            PurchaseRecord.objects.create(customer=self.customer, campaign=self.campaign)
        progress = customer_progress(self.customer, self.campaign)
        self.assertTrue(progress["is_eligible"])

        RewardRedemption.objects.create(customer=self.customer, campaign=self.campaign)
        progress_after_redemption = customer_progress(self.customer, self.campaign)
        self.assertEqual(progress_after_redemption["purchase_count"], 0)
        self.assertFalse(progress_after_redemption["is_eligible"])

    def test_public_lookup_works(self):
        response = self.client.post(reverse("customers:public-lookup"), {"phone": "9999"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("customers:public-progress", kwargs={"pk": self.customer.pk}))

    def test_purchase_association_view_registers_purchase_for_selected_customer(self):
        self.client.login(username="lojista", password="senha-segura-123")
        response = self.client.post(
            reverse("customers:purchase-association"),
            {"customer": self.customer.pk, "notes": "Compra no balcao"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("customers:detail", kwargs={"pk": self.customer.pk}))

        purchase = PurchaseRecord.objects.get(customer=self.customer)
        self.assertEqual(purchase.campaign, self.campaign)
        self.assertEqual(purchase.notes, "Compra no balcao")

    def test_purchase_association_search_returns_matching_customer(self):
        self.client.login(username="lojista", password="senha-segura-123")
        response = self.client.get(
            reverse("customers:purchase-association"),
            {"q": "7777", "mode": "phone"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Marcos")
        self.assertNotContains(response, "Maria")

    def test_purchase_association_can_prefill_selected_customer_from_querystring(self):
        self.client.login(username="lojista", password="senha-segura-123")
        response = self.client.get(
            reverse("customers:purchase-association"),
            {"customer": self.customer.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente selecionado")
        self.assertContains(response, "Maria")
        self.assertContains(response, "2 pet(s)")

    def test_customer_create_view_saves_pet_count(self):
        self.client.login(username="lojista", password="senha-segura-123")
        response = self.client.post(
            reverse("customers:create"),
            {
                "name": "Ana",
                "phone": "11777776666",
                "email": "ana@example.com",
                "pet_count": 4,
            },
        )
        self.assertEqual(response.status_code, 302)
        customer = Customer.objects.get(phone="11777776666")
        self.assertEqual(customer.pet_count, 4)

    def test_login_form_uses_portuguese_labels(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario")
        self.assertContains(response, "Senha")

    def test_customer_form_uses_translated_labels(self):
        self.client.login(username="lojista", password="senha-segura-123")
        response = self.client.get(reverse("customers:create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nome completo")
        self.assertContains(response, "Quantidade de pets")

    def test_customer_list_marks_clients_without_purchase_this_month(self):
        self.client.login(username="lojista", password="senha-segura-123")
        self.create_purchase(self.customer, self.aware_datetime(2026, 6, 12))
        self.create_purchase(self.customer_two, self.aware_datetime(2026, 5, 30))
        Customer.objects.create(name="Bruna", phone="11666665555", email="bruna@example.com", pet_count=3)

        with patch("customers.views.timezone.localdate", return_value=date(2026, 6, 28)):
            response = self.client.get(reverse("customers:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pets")
        self.assertContains(response, "Comprou neste mes")
        self.assertContains(response, "Quase 1 mes sem comprar")
        self.assertContains(response, "Sem compras")
        self.assertContains(response, "<td>2</td>", html=True)
        self.assertContains(response, "<td>3</td>", html=True)

    def test_campaign_form_uses_translated_labels(self):
        self.client.login(username="lojista", password="senha-segura-123")
        response = self.client.get(reverse("loyalty:campaign-settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tipo de regra")
        self.assertContains(response, "Nome do premio")

    def test_monthly_consecutive_unlocks_only_after_final_month_closes(self):
        monthly_campaign = LoyaltyCampaign.objects.create(
            name="Ciclo Mensal",
            rule_type=LoyaltyCampaign.RULE_TYPE_MONTHLY_CONSECUTIVE,
            cycle_length_months=3,
            minimum_purchases_per_month=2,
            reward_name="Banho gratis",
            is_active=True,
        )
        self.create_purchase(self.customer, self.aware_datetime(2026, 1, 5), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 1, 20), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 2, 7), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 2, 18), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 3, 2), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 3, 25), campaign=monthly_campaign)

        with patch("loyalty.services.timezone.localdate", return_value=date(2026, 3, 28)):
            progress_in_final_month = customer_progress(self.customer, monthly_campaign)

        self.assertFalse(progress_in_final_month["is_eligible"])
        self.assertEqual(progress_in_final_month["completed_months"], 2)
        self.assertEqual(progress_in_final_month["current_cycle_month_number"], 3)
        self.assertEqual(progress_in_final_month["current_month_purchases"], 2)
        self.assertEqual(progress_in_final_month["status_label"], "Aguardando fechamento do mes")

        with patch("loyalty.services.timezone.localdate", return_value=date(2026, 4, 1)):
            progress_after_month_close = customer_progress(self.customer, monthly_campaign)

        self.assertTrue(progress_after_month_close["is_eligible"])
        self.assertEqual(progress_after_month_close["completed_months"], 3)
        self.assertEqual(progress_after_month_close["progress_percent"], 100)

    def test_monthly_consecutive_resets_after_month_without_minimum(self):
        monthly_campaign = LoyaltyCampaign.objects.create(
            name="Ciclo Mensal",
            rule_type=LoyaltyCampaign.RULE_TYPE_MONTHLY_CONSECUTIVE,
            cycle_length_months=3,
            minimum_purchases_per_month=2,
            reward_name="Banho gratis",
            is_active=True,
        )
        self.create_purchase(self.customer, self.aware_datetime(2026, 1, 5), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 1, 20), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 2, 7), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 4, 3), campaign=monthly_campaign)

        with patch("loyalty.services.timezone.localdate", return_value=date(2026, 4, 10)):
            progress = customer_progress(self.customer, monthly_campaign)

        self.assertFalse(progress["is_eligible"])
        self.assertEqual(progress["current_cycle_month_number"], 1)
        self.assertEqual(progress["current_month_purchases"], 1)
        self.assertEqual(progress["completed_months"], 0)
        self.assertEqual(progress["current_cycle_started_at"], date(2026, 4, 1))

    def test_monthly_consecutive_resets_after_redemption(self):
        monthly_campaign = LoyaltyCampaign.objects.create(
            name="Ciclo Mensal",
            rule_type=LoyaltyCampaign.RULE_TYPE_MONTHLY_CONSECUTIVE,
            cycle_length_months=2,
            minimum_purchases_per_month=1,
            reward_name="Brinde",
            is_active=True,
        )
        self.create_purchase(self.customer, self.aware_datetime(2026, 1, 5), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 2, 5), campaign=monthly_campaign)
        self.create_redemption(self.customer, self.aware_datetime(2026, 3, 2), campaign=monthly_campaign)
        self.create_purchase(self.customer, self.aware_datetime(2026, 3, 10), campaign=monthly_campaign)

        with patch("loyalty.services.timezone.localdate", return_value=date(2026, 3, 15)):
            progress = customer_progress(self.customer, monthly_campaign)

        self.assertFalse(progress["is_eligible"])
        self.assertEqual(progress["current_cycle_started_at"], date(2026, 3, 1))
        self.assertEqual(progress["current_cycle_month_number"], 1)
        self.assertEqual(progress["current_month_purchases"], 1)

    def test_campaign_form_saves_monthly_configuration(self):
        self.client.login(username="lojista", password="senha-segura-123")
        response = self.client.post(
            reverse("loyalty:campaign-settings"),
            {
                "name": "Ciclo Mensal",
                "description": "Meta por meses",
                "rule_type": LoyaltyCampaign.RULE_TYPE_MONTHLY_CONSECUTIVE,
                "required_purchases": 3,
                "cycle_length_months": 6,
                "minimum_purchases_per_month": 2,
                "reward_name": "Brinde",
                "reward_description": "Descricao",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        campaign = LoyaltyCampaign.get_active()
        self.assertEqual(campaign.rule_type, LoyaltyCampaign.RULE_TYPE_MONTHLY_CONSECUTIVE)
        self.assertEqual(campaign.cycle_length_months, 6)
        self.assertEqual(campaign.minimum_purchases_per_month, 2)

    def test_public_progress_renders_monthly_summary(self):
        monthly_campaign = LoyaltyCampaign.objects.create(
            name="Ciclo Mensal",
            rule_type=LoyaltyCampaign.RULE_TYPE_MONTHLY_CONSECUTIVE,
            cycle_length_months=3,
            minimum_purchases_per_month=2,
            reward_name="Banho gratis",
            is_active=True,
        )
        self.create_purchase(self.customer, self.aware_datetime(2026, 1, 5), campaign=monthly_campaign)

        with patch("loyalty.services.timezone.localdate", return_value=date(2026, 1, 15)):
            response = self.client.get(reverse("customers:public-progress", kwargs={"pk": self.customer.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mês 1 de 3")
        self.assertContains(response, "Meses concluídos")
