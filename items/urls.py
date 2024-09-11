from django.urls import path

from . import views

urlpatterns = [
    path("", views.ItemListView.as_view(), name="item-index"),
    path("create/", views.ItemCreateView.as_view(), name="item-create"),
    path("update/<int:pk>/", views.ItemUpdateView.as_view(), name="item-update"),
    path("<int:pk>/", views.ItemDetailView.as_view(), name="item-detail"),
    path("delete/<int:pk>/", views.ItemDeleteView.as_view(), name="item-delete"),
]
