"""Root URL configuration for the admin dashboard project."""
from django.contrib import admin
from django.urls import include, path

from apps.dashboard.urls import api_urlpatterns

admin.site.site_header = "Company Dashboard"
admin.site.site_title = "Company Admin"
admin.site.index_title = "Administration"

urlpatterns = [
    # Dashboard frontend (login-protected views)
    path("", include("apps.dashboard.urls")),

    # Authentication (login / logout / password reset)
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", __import__("apps.dashboard.views", fromlist=["register_view"]).register_view, name="register"),

    # Django admin
    path("admin/", admin.site.urls),

    # REST API
    path("api/", include(api_urlpatterns)),
]
