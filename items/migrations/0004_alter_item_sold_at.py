# Generated by Django 5.1.1 on 2024-09-10 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0003_alter_cart_checked_out_alter_item_sold_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="sold_at",
            field=models.DateTimeField(null=True),
        ),
    ]
