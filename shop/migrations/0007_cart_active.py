# Generated by Django 4.2.16 on 2024-09-23 22:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0006_remove_order_checked_out_remove_order_items_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="active",
            field=models.BooleanField(default=True),
        ),
    ]
