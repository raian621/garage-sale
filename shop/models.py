"""Models for the shop application."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone


class Item(models.Model):
    """Item model represents an item for sale in the garage sale."""

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    price_in_cents = models.PositiveIntegerField()
    sold_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Model metadata class."""

        ordering = ["id"]

    def __str__(self) -> str:
        """
        Return the Item model's string representation.

        Returns:
            str: String representation of the Item model
        """
        return self.name.__str__()

    def format_price(self) -> str:
        """
        Return the formatted price of the Item ($[dollars].[cents]).

        Returns:
            str: The formatted price of the Item.
        """
        return f"${(self.price_in_cents / 100.0):,.2f}"

    def is_sold(self) -> bool:
        """
        Return whether or not the item has been sold.

        Returns:
            bool: Whether or not the item has been sold.
        """
        return self.sold_at is not None


class Cart(models.Model):
    """Cart model represents a customer's cart."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)
    total_in_cents = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        """
        Return the Item model's string representation.

        Returns:
            str: String representation of the Item model
        """
        return f"Cart {self.id}"

    def add_item(self, item: Item) -> None:
        """
        Add an item to the cart.

        Args:
            item (Item): Item to add to the cart.
        """
        self.total_in_cents += item.price_in_cents
        self.items.add(item)
        self.save()

    def remove_item(self, item: Item) -> None:
        """
        Remove an item from the cart.

        Args:
            item (Item): Item to remove from the cart.
        """
        self.total_in_cents -= item.price_in_cents
        self.items.remove(item)
        self.save()

    def checkout(
        self,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
    ) -> Order:
        """
        Checkout the Cart, creating an Order object in the database.

        Args:
            first_name (str | None): Customer's first name (optional).
            last_name (str | None): Customer's last name (optional).
            email (str | None): Customer's email (optional).

        Returns:
            Order: The Order object created by checking the Cart out.
        """
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

    @staticmethod
    def get_active_cart(user: User) -> Cart:
        """
        Get the active cart for the current User.

        If there is no active cart for the current User, create an active cart
        and return it.

        Args:
            user (User): The current User.

        Returns:
            Cart: The active cart for the current user.
        """
        cart = Cart.objects.filter(user=user, active=True).first()
        if cart is None:
            cart = Cart.objects.create(user=user)
        return cart


class Order(models.Model):
    """Order model represents a Customer's order in the database."""

    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    email = models.EmailField(default="")
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        """Model metadata class."""

        ordering = ["id"]

    def __str__(self) -> str:
        """
        Return the Item model's string representation.

        Returns:
            str: String representation of the Item model
        """
        return f"Order {self.id}"
