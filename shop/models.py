from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from typing import Optional


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


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)
    total_in_cents = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def add_item(self, item: Item):
        self.total_in_cents += item.price_in_cents
        self.items.add(item)
        self.save()

    def remove_item(self, item: Item):
        self.total_in_cents -= item.price_in_cents
        self.items.remove(item)
        self.save()

    def checkout(
        self,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
    ) -> "Order":
        with transaction.atomic():
            created_at = timezone.now()
            order = Order(
                first_name=first_name,
                last_name=last_name,
                email=email,
                created_at=created_at,
                cart=self,
            )
            order.save()
            self.active = False
            for item in self.items.all():
                item.sold_at = created_at
                item.save()
            self.save()
            new_active_cart = Cart(user=self.user)
            new_active_cart.save()
            return order

    def get_active_cart(user) -> "Cart":
        cart = Cart.objects.filter(user=user, active=True).first()
        if cart is None:
            cart = Cart.objects.create(user=user)
        return cart


class Order(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["id"]
