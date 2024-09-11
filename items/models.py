from django.db import models

# Create your models here.


class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    price_in_cents = models.PositiveIntegerField()
    sold_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name.__str__()

    def format_price(self):
        return f"${(self.price_in_cents / 100.0):,.2f}"


class Customer(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"${self.name.__str__()} ({self.id})"


class Cart(models.Model):
    items = models.ManyToManyField(Item)
    customer = models.OneToOneField(Customer, on_delete=models.PROTECT)
    checked_out = models.DateTimeField(blank=True, null=True)

    def add_to_cart(self, item: Item):
        self.items.add(item)
        self.save()

    def remove_from_cart(self, item: Item):
        self.items.remove(item)
        self.save()
