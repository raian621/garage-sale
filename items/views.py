from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Item
from .forms import UpdateItemForm
from django.urls import reverse_lazy


class ItemListView(ListView):
    model = Item
    paginate_by = 20


class ItemDetailView(DetailView):
    model = Item


class ItemCreateView(CreateView):
    model = Item
    fields = ["name", "description", "price_in_cents"]

    def get_success_url(self):
        return reverse_lazy("item-detail", kwargs={"pk": self.kwargs["pk"]})


class ItemUpdateView(UpdateView):
    model = Item
    form_class = UpdateItemForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse_lazy("item-detail", kwargs={"pk": self.kwargs["pk"]})


class ItemDeleteView(DeleteView):
    model = Item
    success_url = reverse_lazy("index")
