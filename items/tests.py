from django.test import TestCase
from .models import Item, Customer, Cart


class ItemModelTests(TestCase):
    def test_format_price(self):
        item = Item(
            name="Taco", description="Senor, this is a taco", price_in_cents=123
        )
        self.assertEqual(item.format_price(), "$1.23")
        item.price_in_cents = 12
        self.assertEqual(item.format_price(), "$0.12")
        item.price_in_cents = 145212
        self.assertEqual(item.format_price(), "$1,452.12")
        item.price_in_cents = 1_000_000_000_000
        self.assertEqual(item.format_price(), "$10,000,000,000.00")


class CartModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.customer = Customer()
        cls.customer.save()
        cls.cart = Cart(customer=cls.customer)
        cls.cart.save()

    @classmethod
    def tearDownClass(cls):
        cls.cart.delete()
        cls.customer.delete()

    def test_add_to_cart(self):
        item = Item(
            name="this is a cool item",
            description="yeah, this is a really cool item",
            price_in_cents=200,
        )
        item.save()
        self.cart.add_to_cart(item)
        self.assertEqual(self.cart.items.all()[0], item)
        item.delete()
        self.assertEqual(self.cart.items.count(), 0)

    def test_remove_from_cart(self):
        item = Item(
            name="this is a cool item",
            description="yeah, this is a really cool item",
            price_in_cents=200,
        )
        item.save()
        self.cart.remove_from_cart(item)
        self.cart.add_to_cart(item)
        self.assertEqual(self.cart.items.count(), 1)
        self.cart.remove_from_cart(item)
        self.assertEqual(self.cart.items.count(), 0)
        item.delete()
