from django.views.generic.list import ListView, View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed
from .models import Item, Order
from .forms import UpdateItemForm, CheckoutForm
from django.urls import reverse, reverse_lazy
from django.shortcuts import render


class ItemListView(ListView):
    model = Item
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(ItemListView, self).get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        objects = page_obj.object_list
        costs = list(map(lambda item: item.format_price(), objects))
        context["object_list"] = zip(objects, costs)
        context["page_obj"] = page_obj
        return context


class ItemDetailView(DetailView):
    model = Item

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context["price_formatted"] = context["object"].format_price()
        return context


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    fields = ["name", "description", "price_in_cents"]

    def get_success_url(self):
        return reverse("item-detail", args=(self.object.id,))


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = UpdateItemForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("item-detail", kwargs={"pk": self.kwargs["pk"]})


class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item
    success_url = reverse_lazy("item-index")


class OrderListView(LoginRequiredMixin, ListView):
    model = Order


def shop_index(request):
    items = Item.objects.all()[:10]
    return render(request, "index.html", context={"items": items})


@login_required
def checkout(request):
    if request.method == "GET":
        return render(
            request, "shop/checkout.html", context={"form": CheckoutForm}
        )
    elif request.method == "POST":
        return HttpResponse("POST")
    return HttpResponseNotAllowed(["GET", "POST"])


def get_items(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    name = request.GET.get("name", None)
    if name:
        items = Item.objects.filter(name__contains=name)[:10]
    else:
        items = Item.objects.all()[:10]
    if len(items) == 0:
        return HttpResponse(
            f"items with name `{name}` not found",
            status=404,
            content_type="application/json",
        )

    return HttpResponse(
        serialize("json", items), content_type="application/json"
    )
