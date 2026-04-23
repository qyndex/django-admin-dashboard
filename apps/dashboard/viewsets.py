"""DRF viewsets for the admin dashboard."""
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Activity, DashboardMetric, Department, Employee, Notification, Project
from .serializers import (
    ActivitySerializer,
    DashboardMetricSerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    NotificationSerializer,
    ProjectSerializer,
)


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


class DashboardMetricViewSet(viewsets.ModelViewSet):
    """CRUD for dashboard metrics."""

    queryset = DashboardMetric.objects.all()
    serializer_class = DashboardMetricSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "value", "created_at"]

    @action(detail=False, methods=["get"], url_path="by-period/(?P<period>[a-z]+)")
    def by_period(self, request: Request, period: str | None = None) -> Response:
        """Return metrics filtered by period."""
        qs = self.get_queryset().filter(period=period)
        serializer = self.get_serializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to activity logs."""

    queryset = Activity.objects.select_related("user").all()
    serializer_class = ActivitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["description", "user__first_name", "user__last_name"]
    ordering_fields = ["created_at", "action"]

    @action(detail=False, methods=["get"], url_path="by-user/(?P<user_id>[0-9]+)")
    def by_user(self, request: Request, user_id: int | None = None) -> Response:
        """Return activities for a specific user."""
        qs = self.get_queryset().filter(user_id=user_id)
        serializer = self.get_serializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})


class NotificationViewSet(viewsets.ModelViewSet):
    """CRUD for notifications — scoped to the authenticated user."""

    serializer_class = NotificationSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "read"]

    def get_queryset(self):
        """Only return notifications for the current user."""
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request: Request, pk=None) -> Response:
        """Mark a single notification as read."""
        notification = self.get_object()
        notification.read = True
        notification.save(update_fields=["read"])
        return Response({"status": "read"})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request: Request) -> Response:
        """Mark all of the user's notifications as read."""
        count = self.get_queryset().filter(read=False).update(read=True)
        return Response({"status": "done", "marked": count})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request: Request) -> Response:
        """Return the count of unread notifications."""
        count = self.get_queryset().filter(read=False).count()
        return Response({"unread_count": count})
