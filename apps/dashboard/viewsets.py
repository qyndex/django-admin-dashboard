"""DRF viewsets for the admin dashboard."""
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Department, Employee, Project
from .serializers import DepartmentSerializer, EmployeeSerializer, ProjectSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """CRUD for departments."""

    queryset = Department.objects.select_related("head").all()
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_at"]


class EmployeeViewSet(viewsets.ModelViewSet):
    """CRUD for employees."""

    queryset = Employee.objects.select_related("user", "department").all()
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__first_name", "user__last_name", "job_title"]
    ordering_fields = ["hire_date", "salary", "created_at"]

    @action(detail=False, methods=["get"], url_path="by-department/(?P<dept_id>[0-9]+)")
    def by_department(self, request: Request, dept_id: int | None = None) -> Response:
        """Return all employees in a specific department."""
        qs = self.get_queryset().filter(department_id=dept_id)
        serializer = self.get_serializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD for projects."""

    queryset = Project.objects.select_related("department").prefetch_related("members").all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["start_date", "budget", "status", "created_at"]

    @action(detail=False, methods=["get"], url_path="active")
    def active_projects(self, request: Request) -> Response:
        """Return only active projects."""
        qs = self.get_queryset().filter(status=Project.STATUS_ACTIVE)
        serializer = self.get_serializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})
