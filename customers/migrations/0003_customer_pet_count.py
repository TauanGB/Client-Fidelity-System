from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="pet_count",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
