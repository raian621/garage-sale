# Generated by Django 4.2.16 on 2024-09-21 15:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0004_alter_item_options_alter_order_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
