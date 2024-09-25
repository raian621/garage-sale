from shop.models import Item, Cart
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User


class ItemModelTests(TestCase):
    def test_format_price(self):
        item = Item(
            name="Taco",
            description="Senor, this is a taco",
            price_in_cents=123,
        )
        self.assertEqual(item.format_price(), "$1.23")
        item.price_in_cents = 12
        self.assertEqual(item.format_price(), "$0.12")
        item.price_in_cents = 145212
        self.assertEqual(item.format_price(), "$1,452.12")
        item.price_in_cents = 1_000_000_000_000
        self.assertEqual(item.format_price(), "$10,000,000,000.00")


class OrderModelTests(TestCase):
    def setUp(self):
        self.items = [
            Item(name="Item 1", description="Description", price_in_cents=100),
            Item(name="Item 2", description="Description", price_in_cents=284),
            Item(name="Item 3", description="Description", price_in_cents=953),
            Item(name="Item 4", description="Description", price_in_cents=145),
            Item(name="Item 5", description="Description", price_in_cents=259),
        ]
        for item in self.items:
            item.save()

    def tearDown(self):
        for item in self.items:
            item.delete()


class CartModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_passwd = "password"
        cls.user = User.objects.create(
            username="test_user", password=cls.user_passwd
        )
        cls.cart = Cart.objects.create(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.cart.delete()
        cls.user.delete()

    def test_add_and_remove_items(self):
        items = [
            Item.objects.create(
                name="Item 1", description="Description 1", price_in_cents=12
            ),
            Item.objects.create(
                name="Item 2", description="Description 2", price_in_cents=34
            ),
        ]
        for item in items:
            self.cart.add_item(item)
        self.assertListEqual(list(self.cart.items.all()), items)
        while items:
            item = items.pop()
            self.cart.remove_item(item)
            self.assertListEqual(list(self.cart.items.all()), items)
            item.delete()

    def test_checkout(self):
        items = [
            Item.objects.create(
                name="Item 1", description="Description 1", price_in_cents=12
            ),
            Item.objects.create(
                name="Item 2", description="Description 2", price_in_cents=34
            ),
        ]
        for item in items:
            self.cart.add_item(item)

        before = timezone.now()
        order = self.cart.checkout("John", "Doe", "john.doe@gmail.com")
        after = timezone.now()

        self.assertGreaterEqual(order.created_at, before)
        self.assertLessEqual(order.created_at, after)
        self.assertListEqual(list(order.cart.items.all()), items)
        self.assertFalse(order.cart.active)
        for item in order.cart.items.all():
            self.assertLessEqual(item.sold_at, after)
            self.assertGreaterEqual(item.sold_at, before)

        order.delete()
        for item in items:
            item.delete()

    def test_get_active_cart(self):
        self.cart.active = False
        self.cart.save()
        cart = Cart.get_active_cart(self.user)
        self.assertTrue(cart.active)
        cart.delete()
        self.cart.active = True
        self.cart.save()
