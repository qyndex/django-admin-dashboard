"""Unit tests for dashboard models."""
import datetime

import pytest

from apps.dashboard.factories import (
    ActivityFactory,
    DashboardMetricFactory,
    DepartmentFactory,
    EmployeeFactory,
    NotificationFactory,
    ProjectFactory,
    UserFactory,
    UserProfileFactory,
)
from apps.dashboard.models import (
    Activity,
    DashboardMetric,
    Department,
    Employee,
    Notification,
    Project,
    UserProfile,
)


@pytest.mark.django_db
class TestDepartmentModel:
    def test_str_includes_code_and_name(self) -> None:
        dept = DepartmentFactory(code="ENG", name="Engineering")
        assert str(dept) == "ENG — Engineering"

    def test_default_ordering_is_by_name(self) -> None:
        DepartmentFactory(name="Zeta", code="Z01")
        DepartmentFactory(name="Alpha", code="A01")
        names = list(Department.objects.values_list("name", flat=True))
        assert names == sorted(names)

    def test_head_is_nullable(self) -> None:
        dept = DepartmentFactory(head=None)
        assert dept.head is None

    def test_unique_code_constraint(self) -> None:
        DepartmentFactory(code="UNQ")
        with pytest.raises(Exception):
            DepartmentFactory(code="UNQ")

    def test_unique_name_constraint(self) -> None:
        DepartmentFactory(name="Finance")
        with pytest.raises(Exception):
            DepartmentFactory(name="Finance")

    def test_employees_reverse_relation(self) -> None:
        dept = DepartmentFactory()
        EmployeeFactory.create_batch(3, department=dept)
        assert dept.employees.count() == 3


@pytest.mark.django_db
class TestEmployeeModel:
    def test_str_shows_full_name_and_job_title(self) -> None:
        user = UserFactory(first_name="Jane", last_name="Doe")
        emp = EmployeeFactory(user=user, job_title="Engineer")
        assert str(emp) == "Jane Doe (Engineer)"

    def test_full_name_property(self) -> None:
        user = UserFactory(first_name="Alice", last_name="Smith")
        emp = EmployeeFactory(user=user)
        assert emp.full_name == "Alice Smith"

    def test_default_status_is_active(self) -> None:
        emp = EmployeeFactory()
        assert emp.status == Employee.STATUS_ACTIVE

    def test_status_choices_are_valid(self) -> None:
        valid = {c[0] for c in Employee.STATUS_CHOICES}
        assert Employee.STATUS_ACTIVE in valid
        assert Employee.STATUS_INACTIVE in valid
        assert Employee.STATUS_ON_LEAVE in valid

    def test_updated_at_changes_on_save(self) -> None:
        emp = EmployeeFactory()
        original = emp.updated_at
        emp.job_title = "Senior Engineer"
        emp.save()
        emp.refresh_from_db()
        assert emp.updated_at >= original

    def test_cascade_delete_removes_employee(self) -> None:
        emp = EmployeeFactory()
        user_id = emp.user.pk
        emp.user.delete()
        assert not Employee.objects.filter(pk=emp.pk).exists()

    def test_department_null_on_department_delete(self) -> None:
        dept = DepartmentFactory()
        emp = EmployeeFactory(department=dept)
        dept.delete()
        emp.refresh_from_db()
        assert emp.department is None


@pytest.mark.django_db
class TestProjectModel:
    def test_str_returns_name(self) -> None:
        project = ProjectFactory(name="Alpha Launch")
        assert str(project) == "Alpha Launch"

    def test_default_status_is_planning(self) -> None:
        project = ProjectFactory()
        assert project.status == Project.STATUS_PLANNING

    def test_end_date_is_optional(self) -> None:
        project = ProjectFactory(end_date=None)
        assert project.end_date is None

    def test_members_many_to_many(self) -> None:
        project = ProjectFactory()
        emp1 = EmployeeFactory()
        emp2 = EmployeeFactory()
        project.members.add(emp1, emp2)
        assert project.members.count() == 2

    def test_default_ordering_is_by_created_at_desc(self) -> None:
        p1 = ProjectFactory(name="First")
        p2 = ProjectFactory(name="Second")
        ids = list(Project.objects.values_list("id", flat=True))
        # Most recently created should appear first
        assert ids[0] == p2.pk

    def test_status_choices_are_valid(self) -> None:
        valid = {c[0] for c in Project.STATUS_CHOICES}
        assert Project.STATUS_PLANNING in valid
        assert Project.STATUS_ACTIVE in valid
        assert Project.STATUS_COMPLETED in valid
        assert Project.STATUS_CANCELLED in valid

    def test_department_null_on_department_delete(self) -> None:
        dept = DepartmentFactory()
        project = ProjectFactory(department=dept)
        dept.delete()
        project.refresh_from_db()
        assert project.department is None


@pytest.mark.django_db
class TestUserProfileModel:
    def test_str_shows_name_and_role(self) -> None:
        user = UserFactory(first_name="Jane", last_name="Doe")
        profile = UserProfileFactory(user=user, role=UserProfile.ROLE_MANAGER)
        assert str(profile) == "Jane Doe (Manager)"

    def test_default_role_is_viewer(self) -> None:
        profile = UserProfileFactory()
        assert profile.role == UserProfile.ROLE_VIEWER

    def test_role_choices(self) -> None:
        valid = {c[0] for c in UserProfile.ROLE_CHOICES}
        assert UserProfile.ROLE_ADMIN in valid
        assert UserProfile.ROLE_MANAGER in valid
        assert UserProfile.ROLE_ANALYST in valid
        assert UserProfile.ROLE_VIEWER in valid

    def test_cascade_delete_on_user(self) -> None:
        profile = UserProfileFactory()
        profile.user.delete()
        assert not UserProfile.objects.filter(pk=profile.pk).exists()

    def test_department_null_on_delete(self) -> None:
        dept = DepartmentFactory()
        profile = UserProfileFactory(department=dept)
        dept.delete()
        profile.refresh_from_db()
        assert profile.department is None


@pytest.mark.django_db
class TestDashboardMetricModel:
    def test_str_shows_name_value_period(self) -> None:
        metric = DashboardMetricFactory(name="Revenue", value=1000.50, period="monthly")
        result = str(metric)
        assert "Revenue" in result
        assert "1000.5" in result
        assert "Monthly" in result

    def test_default_period_is_monthly(self) -> None:
        metric = DashboardMetricFactory()
        assert metric.period == DashboardMetric.PERIOD_MONTHLY

    def test_default_change_percent_is_zero(self) -> None:
        metric = DashboardMetricFactory(change_percent=0)
        assert metric.change_percent == 0

    def test_ordering_is_by_created_at_desc(self) -> None:
        m1 = DashboardMetricFactory(name="First")
        m2 = DashboardMetricFactory(name="Second")
        ids = list(DashboardMetric.objects.values_list("id", flat=True))
        assert ids[0] == m2.pk


@pytest.mark.django_db
class TestActivityModel:
    def test_str_shows_user_and_action(self) -> None:
        user = UserFactory(first_name="Alice", last_name="Smith")
        activity = ActivityFactory(user=user, action=Activity.ACTION_CREATE)
        result = str(activity)
        assert "Alice Smith" in result
        assert "Create" in result

    def test_action_choices(self) -> None:
        valid = {c[0] for c in Activity.ACTION_CHOICES}
        assert Activity.ACTION_LOGIN in valid
        assert Activity.ACTION_CREATE in valid
        assert Activity.ACTION_DELETE in valid

    def test_ip_address_nullable(self) -> None:
        activity = ActivityFactory(ip_address=None)
        assert activity.ip_address is None

    def test_cascade_delete_on_user(self) -> None:
        activity = ActivityFactory()
        activity.user.delete()
        assert not Activity.objects.filter(pk=activity.pk).exists()

    def test_ordering_is_by_created_at_desc(self) -> None:
        a1 = ActivityFactory()
        a2 = ActivityFactory()
        ids = list(Activity.objects.values_list("id", flat=True))
        assert ids[0] == a2.pk


@pytest.mark.django_db
class TestNotificationModel:
    def test_str_shows_read_status_and_title(self) -> None:
        user = UserFactory(first_name="Bob", last_name="Jones")
        notif = NotificationFactory(user=user, title="Alert!", read=False)
        assert "[unread]" in str(notif)
        assert "Alert!" in str(notif)

    def test_str_shows_read_when_read(self) -> None:
        notif = NotificationFactory(read=True, title="Done")
        assert "[read]" in str(notif)

    def test_default_read_is_false(self) -> None:
        notif = NotificationFactory()
        assert notif.read is False

    def test_default_level_is_info(self) -> None:
        notif = NotificationFactory()
        assert notif.level == Notification.LEVEL_INFO

    def test_level_choices(self) -> None:
        valid = {c[0] for c in Notification.LEVEL_CHOICES}
        assert Notification.LEVEL_INFO in valid
        assert Notification.LEVEL_SUCCESS in valid
        assert Notification.LEVEL_WARNING in valid
        assert Notification.LEVEL_ERROR in valid

    def test_cascade_delete_on_user(self) -> None:
        notif = NotificationFactory()
        notif.user.delete()
        assert not Notification.objects.filter(pk=notif.pk).exists()

    def test_ordering_is_by_created_at_desc(self) -> None:
        n1 = NotificationFactory()
        n2 = NotificationFactory()
        ids = list(Notification.objects.values_list("id", flat=True))
        assert ids[0] == n2.pk
