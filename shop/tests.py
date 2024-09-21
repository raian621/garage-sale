from django.test import TestCase
from django.utils.timezone import make_aware
from datetime import datetime, timezone
from django.contrib.auth.models import User
from .models import Item, Order
from .views import ItemListView


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

    def test_calculate_price_in_cents(self):
        order = Order()
        order.save()
        for item in self.items:
            order.add_item(item)
        self.assertEqual(1741, order.total_in_cents)
        for item in self.items:
            order.remove_item(item)
        self.assertEqual(0, order.total_in_cents)
        order.delete()

    def test_checkout(self):
        order = Order()
        order.save()
        for item in self.items:
            order.add_item(item)

        # checkout time should be between timestamps taken before
        # and after the database transaction:
        before = make_aware(datetime.utcnow(), timezone.utc)
        order.checkout()
        during = order.checked_out
        self.assertIsNotNone(during)
        after = make_aware(datetime.utcnow(), timezone.utc)
        self.assertLessEqual(during, after)
        self.assertGreaterEqual(during, before)

        # all items in the order should have the same `sold_at` time
        for item in self.items:
            item.refresh_from_db()
            self.assertIsNotNone(item.sold_at)
            self.assertEqual(item.sold_at, during)
            order.remove_item(item)
        order.delete()


class ItemViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = [
            Item(name="Item 1", description="Description", price_in_cents=100),
            Item(name="Item 2", description="Description", price_in_cents=284),
            Item(name="Item 3", description="Description", price_in_cents=953),
            Item(name="Item 4", description="Description", price_in_cents=145),
            Item(name="Item 5", description="Description", price_in_cents=259),
        ]
        for item in cls.items:
            item.save()

    @classmethod
    def tearDownClass(cls):
        for item in cls.items:
            item.delete()

    def test_get_item_list_request(self):
        res = self.client.get("/shop/")
        self.assertEqual(200, res.status_code)

    def test_get_item_detail_view(self):
        res = self.client.get(f"/shop/{self.items[0].id}/")
        self.assertEqual(200, res.status_code)

    def test_get_item_by_name(self):
        res = self.client.get("/shop/search/?name=Item")
        self.assertEquals(200, res.status_code)
        items = res.json()
        self.assertEquals(len(items), 5)
        res = self.client.get("/shop/search/")
        self.assertEquals(200, res.status_code)
        items = res.json()
        self.assertEquals(len(items), 5)
        res = self.client.get("/shop/search/?name=2")
        self.assertEquals(200, res.status_code)
        items = res.json()
        self.assertEquals(len(items), 1)
        res = self.client.get("/shop/search/?name=mitochondria")
        self.assertEquals(404, res.status_code)


class AuthenticatedItemViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create(username="testuser")
        cls.user.set_password("password")
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_get_item_create_view(self):
        res = self.client.get("/shop/create/")
        # create item page should redirect to the login page if the client
        # isn't authenticated
        self.assertEqual(302, res.status_code)
        self.assertTrue(
            self.client.login(username=self.user.username, password="password")
        )
        res = self.client.get("/shop/create/")
        self.assertEqual(200, res.status_code)

    def test_get_item_update_view(self):
        item = Item(
            name="Item 1", description="Description", price_in_cents=100
        )
        item.save()
        res = self.client.get(f"/shop/{item.id}/update/")
        # create item page should redirect to the login page if the client
        # isn't authenticated
        self.assertEqual(302, res.status_code)
        self.assertTrue(
            self.client.login(username=self.user.username, password="password")
        )
        res = self.client.get(f"/shop/{item.id}/update/")
        self.assertEqual(200, res.status_code)
        item.delete()

    def test_get_checkout_view(self):
        res = self.client.get("/shop/checkout/")
        self.assertTrue(
            self.client.login(username=self.user.username, password="password")
        )
        res = self.client.get("/shop/checkout/")
        self.assertEqual(200, res.status_code)
