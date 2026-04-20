from django.core.exceptions import ValidationError
from django.db import models


class CompanySettings(models.Model):
    THEME_CHOICES = [
        ("classic", "Clássico"),
        ("sunset", "Sunset"),
        ("forest", "Forest"),
    ]

    name = models.CharField("Nome da empresa", max_length=150)
    logo = models.FileField(upload_to="company/logos/", blank=True)
    banner = models.FileField(upload_to="company/banners/", blank=True)
    primary_color = models.CharField(max_length=7, default="#1D4ED8")
    secondary_color = models.CharField(max_length=7, default="#0F172A")
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default="classic")
    description = models.TextField("Descrição", blank=True)
    phone = models.CharField("Telefone", max_length=20, blank=True)
    address = models.CharField("Endereço", max_length=255, blank=True)
    instagram = models.CharField(max_length=255, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração da empresa"
        verbose_name_plural = "Configuração da empresa"

    def clean(self):
        if not self.pk and CompanySettings.objects.exists():
            raise ValidationError("Só é permitido um registro de configuração da empresa por deploy.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @classmethod
    def get_solo(cls):
        return cls.objects.first()
