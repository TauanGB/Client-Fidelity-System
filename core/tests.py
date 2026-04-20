from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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
        self.customer = Customer.objects.create(name="Maria", phone="11999999999", email="maria@example.com")
        self.customer_two = Customer.objects.create(name="Marcos", phone="11888887777", email="marcos@example.com")

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

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
