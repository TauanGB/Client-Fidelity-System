from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("loyalty", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="loyaltycampaign",
            name="cycle_length_months",
            field=models.PositiveIntegerField(default=3),
        ),
        migrations.AddField(
            model_name="loyaltycampaign",
            name="minimum_purchases_per_month",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="loyaltycampaign",
            name="rule_type",
            field=models.CharField(
                choices=[
                    ("purchase_count", "Meta por total de compras"),
                    ("monthly_consecutive", "Ciclo mensal consecutivo"),
                ],
                default="purchase_count",
                max_length=32,
            ),
        ),
    ]
