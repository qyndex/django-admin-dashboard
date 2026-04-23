"""URL routing for the admin dashboard app."""
from rest_framework.routers import DefaultRouter

from .viewsets import DepartmentViewSet, EmployeeViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = router.urls
