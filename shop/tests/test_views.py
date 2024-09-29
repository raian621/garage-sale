from __future__ import annotations

from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from shop.models import Cart, Item, Order
from shop.views import (
    ItemCreateView,
    ItemUpdateView,
    add_item_to_cart,
    checkout,
    remove_item_from_cart,
    shop_index,
)


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
        cls.factory = RequestFactory()

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

    def test_get_index(self):
        request = self.factory.get("/shop/")
        response = shop_index(request)
        self.assertEqual(response.status_code, 200)

    def test_get_item_create_success_url(self):
        request = self.factory.get("/shop/create/")
        view = ItemCreateView()
        view.setup(request)
        view.object = Item.objects.create(
            name="Item", description="Description", price_in_cents=0
        )
        self.assertEqual(view.get_success_url(), f"/shop/{view.object.id}/")
        view.object.delete()

    def test_get_item_update_success_url(self):
        item = Item.objects.create(
            name="Item", description="Description", price_in_cents=0
        )
        request = self.factory.get(f"/shop/{item.id}/update/")
        view = ItemUpdateView()
        view.object = item
        view.setup(request)
        self.assertEqual(view.get_success_url(), f"/shop/{item.id}/")
        item.delete()


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


class CartViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = "password"
        cls.user = User.objects.create_user(
            username="test_user",
            password=cls.password,
        )
        cls.factory = RequestFactory()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.items = [
            Item.objects.create(
                name="Item 1",
                description="Description",
                price_in_cents=110,
            ),
            Item.objects.create(
                name="Item 2",
                description="Description",
                price_in_cents=110,
            ),
            Item.objects.create(
                name="Item 3",
                description="Description",
                price_in_cents=110,
            ),
        ]
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.password
            )
        )

    def tearDown(self):
        for item in self.items:
            item.delete()

    def test_add_item_to_cart(self):
        cart = Cart.get_active_cart(self.user)
        for i, item in enumerate(self.items):
            request = self.factory.post(
                "/shop/cart/add/", {"item_id": item.id}
            )
            request.user = self.user
            res = add_item_to_cart(request)
            self.assertEqual(HTTPStatus.FOUND, res.status_code)
            self.assertEqual(reverse("item-list"), res.headers.get("Location"))
            self.assertListEqual(list(cart.items.all()), self.items[: i + 1])
        cart.delete()

    def test_remove_item_from_cart(self):
        cart = Cart.get_active_cart(self.user)
        for item in self.items:
            cart.add_item(item)
        while self.items:
            item = self.items.pop()
            request = self.factory.post(
                "/shop/cart/remove/", {"item_id": item.id}
            )
            request.user = self.user
            res = remove_item_from_cart(request)
            self.assertEqual(HTTPStatus.FOUND, res.status_code)
            self.assertEqual(reverse("checkout"), res.headers.get("Location"))
            self.assertListEqual(list(cart.items.all()), self.items)
        cart.delete()

    def test_add_sold_item_to_cart(self):
        cart = Cart.get_active_cart(self.user)
        self.items[0].sold_at = timezone.now()
        self.items[0].save()
        for item in self.items:
            request = self.factory.post(
                reverse("cart-add"), {"item_id": item.id}
            )
            request.user = self.user
            res = add_item_to_cart(request)
            if item.is_sold():
                self.assertEqual(HTTPStatus.BAD_REQUEST, res.status_code)
            else:
                self.assertEqual(HTTPStatus.FOUND, res.status_code)
        self.assertListEqual(list(cart.items.all()), self.items[1:])
        cart.delete()

    def test_remove_item_not_in_cart(self):
        not_in_cart = Item.objects.create(
            name="THE Item", description="THE description", price_in_cents=100
        )
        request = self.factory.post(
            reverse("cart-remove"), {"item_id": not_in_cart.id}
        )
        request.user = self.user
        res = remove_item_from_cart(request)
        self.assertEqual(HTTPStatus.BAD_REQUEST, res.status_code)

    def test_checkout(self):
        cart = Cart.get_active_cart(self.user)
        for item in self.items:
            cart.add_item(item)
        first_name = "John"
        last_name = "Doe"
        email = "john.doe@gmail.com"
        request = self.factory.post(
            "/shop/checkout/",
            data={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            },
        )
        request.user = self.user
        before = timezone.now()
        res = checkout(request)
        after = timezone.now()
        self.assertEqual(HTTPStatus.FOUND, res.status_code)
        cart.refresh_from_db()
        self.assertFalse(cart.active)
        order = Order.objects.get(cart=cart)
        self.assertLessEqual(order.created_at, after)
        self.assertGreaterEqual(order.created_at, before)
        for item in self.items:
            item.refresh_from_db()
            self.assertLessEqual(item.sold_at, after)
            self.assertGreaterEqual(item.sold_at, before)
        order.delete()
        cart.delete()
