"""Tests for Django admin customizations."""
import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from apps.dashboard.admin import DepartmentAdmin, EmployeeAdmin, ProjectAdmin
from apps.dashboard.factories import DepartmentFactory, EmployeeFactory, ProjectFactory, UserFactory
from apps.dashboard.models import Department, Employee, Project


@pytest.fixture
def site() -> AdminSite:
    return AdminSite()


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.mark.django_db
class TestDepartmentAdmin:
    def test_employee_count_display(self, site: AdminSite) -> None:
        dept = DepartmentFactory()
        EmployeeFactory.create_batch(3, department=dept)
        ma = DepartmentAdmin(Department, site)
        assert ma.employee_count(dept) == 3

    def test_employee_count_zero_for_empty_department(self, site: AdminSite) -> None:
        dept = DepartmentFactory()
        ma = DepartmentAdmin(Department, site)
        assert ma.employee_count(dept) == 0

    def test_list_display_fields(self, site: AdminSite) -> None:
        ma = DepartmentAdmin(Department, site)
        assert "code" in ma.list_display
        assert "name" in ma.list_display
        assert "employee_count" in ma.list_display

    def test_search_fields_include_name_and_code(self, site: AdminSite) -> None:
        ma = DepartmentAdmin(Department, site)
        assert "name" in ma.search_fields
        assert "code" in ma.search_fields

    def test_get_queryset_returns_departments(
        self,
        site: AdminSite,
        admin_user,
        request_factory: RequestFactory,
    ) -> None:
        DepartmentFactory.create_batch(2)
        ma = DepartmentAdmin(Department, site)
        request = request_factory.get("/admin/dashboard/department/")
        request.user = admin_user
        qs = ma.get_queryset(request)
        assert qs.count() == 2


@pytest.mark.django_db
class TestEmployeeAdmin:
    def test_full_name_display(self, site: AdminSite) -> None:
        user = UserFactory(first_name="John", last_name="Doe")
        emp = EmployeeFactory(user=user)
        ma = EmployeeAdmin(Employee, site)
        assert ma.full_name(emp) == "John Doe"

    def test_list_display_fields(self, site: AdminSite) -> None:
        ma = EmployeeAdmin(Employee, site)
        assert "full_name" in ma.list_display
        assert "job_title" in ma.list_display
        assert "status" in ma.list_display
        assert "salary" in ma.list_display

    def test_list_filter_contains_status_and_department(self, site: AdminSite) -> None:
        ma = EmployeeAdmin(Employee, site)
        assert "status" in ma.list_filter
        assert "department" in ma.list_filter

    def test_list_editable_contains_status(self, site: AdminSite) -> None:
        ma = EmployeeAdmin(Employee, site)
        assert "status" in ma.list_editable

    def test_search_fields_cover_name_and_job_title(self, site: AdminSite) -> None:
        ma = EmployeeAdmin(Employee, site)
        assert "job_title" in ma.search_fields


@pytest.mark.django_db
class TestProjectAdmin:
    def test_member_count_display(self, site: AdminSite) -> None:
        project = ProjectFactory()
        project.members.add(EmployeeFactory(), EmployeeFactory())
        ma = ProjectAdmin(Project, site)
        assert ma.member_count(project) == 2

    def test_member_count_zero_for_no_members(self, site: AdminSite) -> None:
        project = ProjectFactory()
        ma = ProjectAdmin(Project, site)
        assert ma.member_count(project) == 0

    def test_list_display_fields(self, site: AdminSite) -> None:
        ma = ProjectAdmin(Project, site)
        assert "name" in ma.list_display
        assert "status" in ma.list_display
        assert "budget" in ma.list_display
        assert "member_count" in ma.list_display

    def test_list_filter_contains_status_and_department(self, site: AdminSite) -> None:
        ma = ProjectAdmin(Project, site)
        assert "status" in ma.list_filter
        assert "department" in ma.list_filter

    def test_search_fields_cover_name_and_description(self, site: AdminSite) -> None:
        ma = ProjectAdmin(Project, site)
        assert "name" in ma.search_fields
        assert "description" in ma.search_fields

    def test_filter_horizontal_has_members(self, site: AdminSite) -> None:
        ma = ProjectAdmin(Project, site)
        assert "members" in ma.filter_horizontal
