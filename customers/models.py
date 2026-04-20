import uuid

from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    public_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PurchaseRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="purchase_records")
    campaign = models.ForeignKey("loyalty.LoyaltyCampaign", on_delete=models.CASCADE, related_name="purchase_records")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer} - {self.created_at:%d/%m/%Y %H:%M}"
