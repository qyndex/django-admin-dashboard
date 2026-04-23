"""Root URL configuration for the admin dashboard project."""
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Company Dashboard"
admin.site.site_title = "Company Admin"
admin.site.index_title = "Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.dashboard.urls")),
]
