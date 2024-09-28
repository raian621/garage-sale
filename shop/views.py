"""Views for the shop application."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import CheckoutForm, UpdateItemForm
from .models import Cart, Item, Order

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ItemListView(ListView):
    """List view used to display and paginate Items."""

    model = Item
    paginate_by = 20

    def get_context_data(self, **kwargs: dict) -> dict[str, any]:
        """
        Get context data object used to render the view template.

        Args:
            kwargs (dict[str, any]): Keyword arguments.

        Returns:
            dict[str, any]: The context data object used to render the view
            template.
        """
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        objects = page_obj.object_list
        costs = [item.format_price() for item in objects]
        sold = [item.is_sold() for item in objects]
        context["object_list"] = list(zip(objects, costs, sold))
        context["page_obj"] = page_obj
        return context

    def get_queryset(self) -> QuerySet:
        """
        Get the queryset used to paginate Item models.

        Returns:
            QuerySet: Queryset used to paginate the Item models.
        """
        filter_val = self.request.GET.get("filter")
        include_sold = self.request.GET.get("include_sold")
        if include_sold == "true" and filter_val and len(filter_val) > 0:
            return Item.objects.filter(name__contains=filter_val)
        if include_sold == "true" and (
            filter_val is None or len(filter_val) == 0
        ):
            return Item.objects.all()
        if include_sold is None and filter_val and len(filter_val) > 0:
            return Item.objects.filter(
                name__contains=filter_val, sold_at__isnull=True
            )
        return Item.objects.filter(sold_at__isnull=True)


class ItemDetailView(DetailView):
    """Detail view for the Item model."""

    model = Item

    def get_context_data(self, **kwargs: dict) -> dict[str, any]:
        """
        Get context data object used to render the view template.

        Args:
            kwargs (dict[str, any]): Keyword arguments.

        Returns:
            dict[str, any]: The context data object used to render the view
            template.
        """
        context = super().get_context_data(**kwargs)
        context["price_formatted"] = context["object"].format_price()
        return context


class ItemCreateView(LoginRequiredMixin, CreateView):
    """View used to create Item models in the database."""

    model = Item
    fields = ["name", "description", "price_in_cents"]

    def get_success_url(self) -> str:
        """
        Get the URL that the view should redirect to upon success.

        Returns:
            str: URL to redirect to.
        """
        return reverse("item-detail", args=(self.object.id,))


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    """View used to update an Item model in the database."""

    model = Item
    form_class = UpdateItemForm
    template_name_suffix = "_update_form"

    def get_success_url(self) -> str:
        """
        Get the URL that the view should redirect to upon success.

        Returns:
            str: URL to redirect to.
        """
        return reverse("item-detail", args=(self.object.id,))


class ItemDeleteView(LoginRequiredMixin, DeleteView):
    """View used to delete an Item model from the database."""

    model = Item
    success_url = reverse_lazy("item-index")


class OrderListView(LoginRequiredMixin, ListView):
    """List view for the Order model."""

    model = Order


def shop_index(request: HttpRequest) -> HttpResponse:
    """
    Shop dashboard view.

    Args:
        request (HttpRequest): The HTTP request to this view.

    Returns:
        response (HttpResponse): The HTTP response to the request.
    """
    items = Item.objects.all()[:10]
    return render(request, "index.html", context={"items": items})


@login_required
def add_item_to_cart(request: HttpRequest) -> HttpResponse:
    """
    View used to add an item to the currently active cart.

    Args:
        request (HttpRequest): The HTTP request to this view.

    Returns:
        response (HttpResponse): The HTTP response to the request.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    cart = Cart.get_active_cart(request.user)
    item = Item.objects.get(id=request.POST.get("item_id"))
    cart.add_item(item)
    return redirect(reverse("item-list"))


@login_required
def remove_item_from_cart(request: HttpRequest) -> HttpResponse:
    """
    View used to remove an item from the currently active cart.

    Args:
        request (HttpRequest): The HTTP request to this view.

    Returns:
        response (HttpResponse): The HTTP response to the request.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    cart = Cart.get_active_cart(request.user)
    item = Item.objects.get(id=request.POST.get("item_id"))
    cart.remove_item(item)
    return redirect(reverse("item-list"))


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """
    View for checking out a customer.

    Args:
        request (HttpRequest): The HTTP request to this view.

    Returns:
        HttpResponse: the response to the HTTP request.
    """
    cart = Cart.get_active_cart(request.user)
    if request.method == "GET":
        return render(
            request,
            "shop/checkout.html",
            context={
                "form": CheckoutForm,
                "cart_items": list(cart.items.all()),
            },
        )
    if request.method == "POST":
        cart.checkout(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            email=request.POST.get("email"),
        )
        return redirect(reverse("item-list"))
    return HttpResponseNotAllowed(["GET", "POST"])
