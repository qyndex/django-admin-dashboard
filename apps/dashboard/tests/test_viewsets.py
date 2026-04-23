"""Integration tests for DRF viewsets."""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.dashboard.factories import (
    ActivityFactory,
    DashboardMetricFactory,
    DepartmentFactory,
    EmployeeFactory,
    NotificationFactory,
    ProjectFactory,
    UserFactory,
)
from apps.dashboard.models import Department, Employee, Notification, Project


@pytest.mark.django_db
class TestDepartmentViewSet:
    """Tests for /api/departments/ endpoints."""

    def test_list_returns_all_departments(self, authed_client: APIClient) -> None:
        DepartmentFactory.create_batch(3)
        res = authed_client.get("/api/departments/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 3

    def test_retrieve_single_department(self, authed_client: APIClient) -> None:
        dept = DepartmentFactory(name="Engineering", code="ENG")
        res = authed_client.get(f"/api/departments/{dept.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["name"] == "Engineering"
        assert res.data["code"] == "ENG"

    def test_create_department(self, authed_client: APIClient, admin_user) -> None:
        payload = {"name": "New Dept", "code": "NEW", "head": admin_user.pk}
        res = authed_client.post("/api/departments/", payload, format="json")
        assert res.status_code == status.HTTP_201_CREATED
        assert Department.objects.filter(code="NEW").exists()

    def test_update_department(self, authed_client: APIClient, admin_user) -> None:
        dept = DepartmentFactory()
        payload = {"name": "Updated", "code": dept.code, "head": admin_user.pk}
        res = authed_client.put(f"/api/departments/{dept.pk}/", payload, format="json")
        assert res.status_code == status.HTTP_200_OK
        dept.refresh_from_db()
        assert dept.name == "Updated"

    def test_partial_update_department(self, authed_client: APIClient) -> None:
        dept = DepartmentFactory()
        res = authed_client.patch(f"/api/departments/{dept.pk}/", {"name": "Patched"}, format="json")
        assert res.status_code == status.HTTP_200_OK
        dept.refresh_from_db()
        assert dept.name == "Patched"

    def test_delete_department(self, authed_client: APIClient) -> None:
        dept = DepartmentFactory()
        res = authed_client.delete(f"/api/departments/{dept.pk}/")
        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert not Department.objects.filter(pk=dept.pk).exists()

    def test_search_by_name(self, authed_client: APIClient) -> None:
        DepartmentFactory(name="Engineering", code="ENG")
        DepartmentFactory(name="Marketing", code="MKT")
        res = authed_client.get("/api/departments/?search=Engine")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 1
        assert res.data["results"][0]["name"] == "Engineering"

    def test_unauthenticated_returns_401(self, api_client: APIClient) -> None:
        res = api_client.get("/api/departments/")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_response_includes_employee_count(self, authed_client: APIClient) -> None:
        dept = DepartmentFactory()
        EmployeeFactory.create_batch(2, department=dept)
        res = authed_client.get(f"/api/departments/{dept.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["employee_count"] == 2


@pytest.mark.django_db
class TestEmployeeViewSet:
    """Tests for /api/employees/ endpoints."""

    def test_list_returns_all_employees(self, authed_client: APIClient) -> None:
        EmployeeFactory.create_batch(4)
        res = authed_client.get("/api/employees/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 4

    def test_retrieve_employee_includes_full_name(self, authed_client: APIClient) -> None:
        user = UserFactory(first_name="Bob", last_name="Builder")
        emp = EmployeeFactory(user=user, job_title="Constructor")
        res = authed_client.get(f"/api/employees/{emp.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["full_name"] == "Bob Builder"
        assert res.data["job_title"] == "Constructor"

    def test_create_employee(self, authed_client: APIClient) -> None:
        user = UserFactory()
        dept = DepartmentFactory()
        import datetime
        payload = {
            "user": user.pk,
            "department": dept.pk,
            "job_title": "Analyst",
            "salary": "60000.00",
            "status": Employee.STATUS_ACTIVE,
            "hire_date": str(datetime.date.today()),
        }
        res = authed_client.post("/api/employees/", payload, format="json")
        assert res.status_code == status.HTTP_201_CREATED
        assert Employee.objects.filter(user=user).exists()

    def test_update_status(self, authed_client: APIClient) -> None:
        emp = EmployeeFactory(status=Employee.STATUS_ACTIVE)
        res = authed_client.patch(
            f"/api/employees/{emp.pk}/",
            {"status": Employee.STATUS_INACTIVE},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        emp.refresh_from_db()
        assert emp.status == Employee.STATUS_INACTIVE

    def test_delete_employee(self, authed_client: APIClient) -> None:
        emp = EmployeeFactory()
        res = authed_client.delete(f"/api/employees/{emp.pk}/")
        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert not Employee.objects.filter(pk=emp.pk).exists()

    def test_by_department_action(self, authed_client: APIClient) -> None:
        dept = DepartmentFactory()
        EmployeeFactory.create_batch(2, department=dept)
        EmployeeFactory()  # different department
        res = authed_client.get(f"/api/employees/by-department/{dept.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 2

    def test_search_by_last_name(self, authed_client: APIClient) -> None:
        user = UserFactory(last_name="Uniqueson")
        EmployeeFactory(user=user)
        EmployeeFactory()  # different user
        res = authed_client.get("/api/employees/?search=Uniqueson")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 1

    def test_unauthenticated_returns_403(self, api_client: APIClient) -> None:
        res = api_client.get("/api/employees/")
        assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProjectViewSet:
    """Tests for /api/projects/ endpoints."""

    def test_list_returns_all_projects(self, authed_client: APIClient) -> None:
        ProjectFactory.create_batch(3)
        res = authed_client.get("/api/projects/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 3

    def test_retrieve_project_includes_member_count(self, authed_client: APIClient) -> None:
        project = ProjectFactory()
        project.members.add(EmployeeFactory(), EmployeeFactory())
        res = authed_client.get(f"/api/projects/{project.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["member_count"] == 2

    def test_create_project(self, authed_client: APIClient) -> None:
        import datetime
        dept = DepartmentFactory()
        payload = {
            "name": "New Initiative",
            "description": "A new project",
            "department": dept.pk,
            "status": Project.STATUS_PLANNING,
            "budget": "50000.00",
            "start_date": str(datetime.date.today()),
        }
        res = authed_client.post("/api/projects/", payload, format="json")
        assert res.status_code == status.HTTP_201_CREATED
        assert Project.objects.filter(name="New Initiative").exists()

    def test_update_project_status(self, authed_client: APIClient) -> None:
        project = ProjectFactory(status=Project.STATUS_PLANNING)
        res = authed_client.patch(
            f"/api/projects/{project.pk}/",
            {"status": Project.STATUS_ACTIVE},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.status == Project.STATUS_ACTIVE

    def test_delete_project(self, authed_client: APIClient) -> None:
        project = ProjectFactory()
        res = authed_client.delete(f"/api/projects/{project.pk}/")
        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(pk=project.pk).exists()

    def test_active_projects_action_filters_correctly(self, authed_client: APIClient) -> None:
        ProjectFactory(status=Project.STATUS_ACTIVE)
        ProjectFactory(status=Project.STATUS_ACTIVE)
        ProjectFactory(status=Project.STATUS_PLANNING)
        ProjectFactory(status=Project.STATUS_COMPLETED)
        res = authed_client.get("/api/projects/active/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 2
        for item in res.data["results"]:
            assert item["status"] == Project.STATUS_ACTIVE

    def test_search_by_name(self, authed_client: APIClient) -> None:
        ProjectFactory(name="Alpha Initiative")
        ProjectFactory(name="Beta Programme")
        res = authed_client.get("/api/projects/?search=Alpha")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 1
        assert "Alpha" in res.data["results"][0]["name"]

    def test_unauthenticated_returns_403(self, api_client: APIClient) -> None:
        res = api_client.get("/api/projects/")
        assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDashboardMetricViewSet:
    """Tests for /api/metrics/ endpoints."""

    def test_list_returns_all_metrics(self, authed_client: APIClient) -> None:
        DashboardMetricFactory.create_batch(3)
        res = authed_client.get("/api/metrics/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 3

    def test_retrieve_single_metric(self, authed_client: APIClient) -> None:
        metric = DashboardMetricFactory(name="Revenue", value=50000)
        res = authed_client.get(f"/api/metrics/{metric.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["name"] == "Revenue"

    def test_by_period_action(self, authed_client: APIClient) -> None:
        DashboardMetricFactory(period="monthly")
        DashboardMetricFactory(period="monthly")
        DashboardMetricFactory(period="weekly")
        res = authed_client.get("/api/metrics/by-period/monthly/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 2

    def test_unauthenticated_returns_403(self, api_client: APIClient) -> None:
        res = api_client.get("/api/metrics/")
        assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestActivityViewSet:
    """Tests for /api/activities/ endpoints (read-only)."""

    def test_list_returns_all_activities(self, authed_client: APIClient) -> None:
        ActivityFactory.create_batch(3)
        res = authed_client.get("/api/activities/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 3

    def test_retrieve_activity(self, authed_client: APIClient) -> None:
        activity = ActivityFactory(description="Test action")
        res = authed_client.get(f"/api/activities/{activity.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["description"] == "Test action"

    def test_by_user_action(self, authed_client: APIClient) -> None:
        user = UserFactory()
        ActivityFactory.create_batch(2, user=user)
        ActivityFactory()  # different user
        res = authed_client.get(f"/api/activities/by-user/{user.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 2

    def test_create_not_allowed(self, authed_client: APIClient, admin_user) -> None:
        payload = {"user": admin_user.pk, "action": "login", "description": "test"}
        res = authed_client.post("/api/activities/", payload, format="json")
        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_unauthenticated_returns_403(self, api_client: APIClient) -> None:
        res = api_client.get("/api/activities/")
        assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestNotificationViewSet:
    """Tests for /api/notifications/ endpoints."""

    def test_list_returns_only_own_notifications(self, authed_client: APIClient, admin_user) -> None:
        NotificationFactory.create_batch(2, user=admin_user)
        NotificationFactory()  # different user
        res = authed_client.get("/api/notifications/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 2

    def test_mark_read_action(self, authed_client: APIClient, admin_user) -> None:
        notif = NotificationFactory(user=admin_user, read=False)
        res = authed_client.post(f"/api/notifications/{notif.pk}/mark-read/")
        assert res.status_code == status.HTTP_200_OK
        notif.refresh_from_db()
        assert notif.read is True

    def test_mark_all_read_action(self, authed_client: APIClient, admin_user) -> None:
        NotificationFactory.create_batch(3, user=admin_user, read=False)
        res = authed_client.post("/api/notifications/mark-all-read/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["marked"] == 3
        assert Notification.objects.filter(user=admin_user, read=False).count() == 0

    def test_unread_count_action(self, authed_client: APIClient, admin_user) -> None:
        NotificationFactory.create_batch(2, user=admin_user, read=False)
        NotificationFactory(user=admin_user, read=True)
        res = authed_client.get("/api/notifications/unread-count/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["unread_count"] == 2

    def test_unauthenticated_returns_403(self, api_client: APIClient) -> None:
        res = api_client.get("/api/notifications/")
        assert res.status_code == status.HTTP_403_FORBIDDEN
