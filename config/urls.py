"""Root URL configuration for the admin dashboard project."""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from apps.dashboard.urls import api_urlpatterns

admin.site.site_header = "Company Dashboard"
admin.site.site_title = "Company Admin"
admin.site.index_title = "Administration"


def healthz(_request):
    """Unauthenticated liveness probe — returns 200 OK as soon as Django is
    importable and the WSGI app is responding. Used by Coolify / Traefik so
    health checks don't bounce through Django's @login_required redirect."""
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    # Liveness probe (unauthenticated, returns 200)
    path("healthz", healthz, name="healthz"),
    path("healthz/", healthz),

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
