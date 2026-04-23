"""DRF serializers for the admin dashboard app."""
from rest_framework import serializers

from .models import Department, Employee, Project


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department."""

    employee_count = serializers.IntegerField(source="employees.count", read_only=True)
    head_name = serializers.CharField(source="head.get_full_name", read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "code", "head", "head_name", "employee_count", "created_at"]
        read_only_fields = ["id", "created_at"]


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee."""

    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "email",
            "department",
            "department_name",
            "job_title",
            "salary",
            "status",
            "hire_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project."""

    department_name = serializers.CharField(source="department.name", read_only=True)
    member_count = serializers.IntegerField(source="members.count", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "department",
            "department_name",
            "status",
            "budget",
            "start_date",
            "end_date",
            "member_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
