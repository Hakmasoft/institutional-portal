from django.contrib import admin
from django.urls import include, path

from .views import db_health, health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("health/", health, name="health"),
    path("health/db/", db_health, name="db_health"),
    path("", include("portal.urls")),
]
