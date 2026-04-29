from django.core.exceptions import ValidationError
from django.db import models


class LoyaltyCampaign(models.Model):
    RULE_TYPE_PURCHASE_COUNT = "purchase_count"
    RULE_TYPE_MONTHLY_CONSECUTIVE = "monthly_consecutive"
    RULE_TYPE_CHOICES = [
        (RULE_TYPE_PURCHASE_COUNT, "Meta por total de compras"),
        (RULE_TYPE_MONTHLY_CONSECUTIVE, "Ciclo mensal consecutivo"),
    ]

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=32, choices=RULE_TYPE_CHOICES, default=RULE_TYPE_PURCHASE_COUNT)
    required_purchases = models.PositiveIntegerField(default=10)
    cycle_length_months = models.PositiveIntegerField(default=3)
    minimum_purchases_per_month = models.PositiveIntegerField(default=1)
    reward_name = models.CharField(max_length=150)
    reward_description = models.TextField(blank=True)
    reward_image = models.FileField(upload_to="rewards/", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Campanha de fidelidade"
        verbose_name_plural = "Campanhas de fidelidade"

    def clean(self):
        if self.rule_type == self.RULE_TYPE_PURCHASE_COUNT and self.required_purchases < 1:
            raise ValidationError("A campanha deve exigir pelo menos 1 compra.")
        if self.rule_type == self.RULE_TYPE_MONTHLY_CONSECUTIVE:
            if self.cycle_length_months < 1:
                raise ValidationError("O ciclo mensal deve ter pelo menos 1 mes.")
            if self.minimum_purchases_per_month < 1:
                raise ValidationError("A campanha deve exigir pelo menos 1 compra por mes.")

    def save(self, *args, **kwargs):
        self.full_clean()
        result = super().save(*args, **kwargs)
        if self.is_active:
            LoyaltyCampaign.objects.exclude(pk=self.pk).update(is_active=False)
        return result

    def __str__(self):
        return self.name

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first() or cls.objects.first()

    @property
    def is_monthly_consecutive(self):
        return self.rule_type == self.RULE_TYPE_MONTHLY_CONSECUTIVE


class ThemePreset(models.Model):
    name = models.CharField(max_length=100)
    primary_color = models.CharField(max_length=7)
    secondary_color = models.CharField(max_length=7)
    css_class = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"

    def __str__(self):
        return self.name


class RewardRedemption(models.Model):
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="reward_redemptions")
    campaign = models.ForeignKey(LoyaltyCampaign, on_delete=models.CASCADE, related_name="reward_redemptions")
    redeemed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Resgate"
        verbose_name_plural = "Resgates"
        ordering = ["-redeemed_at"]

    def __str__(self):
        return f"{self.customer} - {self.campaign}"
