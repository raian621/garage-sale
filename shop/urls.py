from django.urls import path

from . import views

urlpatterns = [
    path("", views.ItemListView.as_view(), name="item-index"),
    path("create/", views.ItemCreateView.as_view(), name="item-create"),
    path(
        "<int:pk>/update/", views.ItemUpdateView.as_view(), name="item-update"
    ),
    path("<int:pk>/", views.ItemDetailView.as_view(), name="item-detail"),
    path(
        "<int:pk>/delete/", views.ItemDeleteView.as_view(), name="item-delete"
    ),
    path("checkout/", views.checkout, name="checkout"),
    path("search/", views.get_items, name="search"),
]
