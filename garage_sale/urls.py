"""URLs for the garage sale application views."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from shop.views import shop_index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("shop/", include("shop.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", shop_index, name="shop-index"),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]
