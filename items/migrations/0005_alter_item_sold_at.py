# Generated by Django 5.1.1 on 2024-09-11 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0004_alter_item_sold_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="sold_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
