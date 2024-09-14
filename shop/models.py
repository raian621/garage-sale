from django.db import models, transaction
from django.utils.timezone import make_aware
from datetime import datetime, timezone

# Create your models here.


class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    price_in_cents = models.PositiveIntegerField()
    sold_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name.__str__()

    def format_price(self):
        return f"${(self.price_in_cents / 100.0):,.2f}"


class Order(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    items = models.ManyToManyField(Item)
    total_in_cents = models.PositiveIntegerField(default=0)
    checked_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def add_item(self, item: Item):
        self.total_in_cents += item.price_in_cents
        self.items.add(item)

    def remove_item(self, item: Item):
        self.total_in_cents -= item.price_in_cents
        self.items.remove(item)

    def checkout(self):
        with transaction.atomic():
            now = make_aware(datetime.utcnow(), timezone.utc)
            self.checked_out = now
            for item in self.items.all():
                item.sold_at = now
                item.save()
            self.save()
