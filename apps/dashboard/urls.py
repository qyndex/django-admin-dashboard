"""URL routing for the admin dashboard app."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import (
    ActivityViewSet,
    DashboardMetricViewSet,
    DepartmentViewSet,
    EmployeeViewSet,
    NotificationViewSet,
    ProjectViewSet,
)

app_name = "dashboard"

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"metrics", DashboardMetricViewSet, basename="metric")
router.register(r"activities", ActivityViewSet, basename="activity")
router.register(r"notifications", NotificationViewSet, basename="notification")

# Dashboard frontend views
urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="notification-read"),
    path("notifications/read-all/", views.mark_all_notifications_read, name="notifications-read-all"),
    path("activity/", views.activity_log_view, name="activity-log"),
]

# API URLs are included separately in config/urls.py via router.urls
api_urlpatterns = router.urls
