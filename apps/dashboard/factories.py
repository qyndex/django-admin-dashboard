"""Factory Boy factories for the admin dashboard models."""
import datetime

import factory
from django.contrib.auth.models import User

from .models import Department, Employee, Project


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
