from django.contrib import admin
from django.urls import path
from .views import health, db_health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("health/db/", db_health, name="db_health"),
]
