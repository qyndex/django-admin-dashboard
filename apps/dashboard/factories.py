"""Factory Boy factories for the admin dashboard models."""
import datetime

import factory
from django.contrib.auth.models import User

from .models import (
    Activity,
    DashboardMetric,
    Department,
    Employee,
    Notification,
    Project,
    UserProfile,
)


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for Django's built-in User model."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class DepartmentFactory(factory.django.DjangoModelFactory):
    """Factory for Department."""

    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"Department {n}")
    code = factory.Sequence(lambda n: f"D{n:03d}")
    head = factory.SubFactory(UserFactory)


class EmployeeFactory(factory.django.DjangoModelFactory):
    """Factory for Employee."""

    class Meta:
        model = Employee

    user = factory.SubFactory(UserFactory)
    department = factory.SubFactory(DepartmentFactory)
    job_title = factory.Faker("job")
    salary = factory.Faker("pydecimal", left_digits=6, right_digits=2, positive=True)
    status = Employee.STATUS_ACTIVE
    hire_date = factory.LazyFunction(datetime.date.today)


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for Project."""

    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Faker("paragraph")
    department = factory.SubFactory(DepartmentFactory)
    status = Project.STATUS_PLANNING
    budget = factory.Faker("pydecimal", left_digits=8, right_digits=2, positive=True)
    start_date = factory.LazyFunction(datetime.date.today)
    end_date = None


class UserProfileFactory(factory.django.DjangoModelFactory):
    """Factory for UserProfile."""

    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    role = UserProfile.ROLE_VIEWER
    department = factory.SubFactory(DepartmentFactory)


class DashboardMetricFactory(factory.django.DjangoModelFactory):
    """Factory for DashboardMetric."""

    class Meta:
        model = DashboardMetric

    name = factory.Sequence(lambda n: f"Metric {n}")
    value = factory.Faker("pydecimal", left_digits=6, right_digits=2, positive=True)
    change_percent = factory.Faker("pydecimal", left_digits=2, right_digits=2)
    period = DashboardMetric.PERIOD_MONTHLY


class ActivityFactory(factory.django.DjangoModelFactory):
    """Factory for Activity."""

    class Meta:
        model = Activity

    user = factory.SubFactory(UserFactory)
    action = Activity.ACTION_CREATE
    description = factory.Faker("sentence")
    ip_address = factory.Faker("ipv4")


class NotificationFactory(factory.django.DjangoModelFactory):
    """Factory for Notification."""

    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=4)
    message = factory.Faker("paragraph")
    level = Notification.LEVEL_INFO
    read = False
