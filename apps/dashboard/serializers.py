"""DRF serializers for the admin dashboard app."""
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Activity,
    DashboardMetric,
    Department,
    Employee,
    Notification,
    Project,
    UserProfile,
)


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
            "user",
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


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile."""

    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "full_name",
            "email",
            "avatar",
            "role",
            "department",
            "department_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_full_name(self, obj) -> str:
        return obj.user.get_full_name()


class DashboardMetricSerializer(serializers.ModelSerializer):
    """Serializer for DashboardMetric."""

    class Meta:
        model = DashboardMetric
        fields = ["id", "name", "value", "change_percent", "period", "icon", "created_at"]
        read_only_fields = ["id", "created_at"]


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity."""

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = Activity
        fields = ["id", "user", "user_name", "action", "action_display", "description", "ip_address", "created_at"]
        read_only_fields = ["id", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification."""

    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "user", "title", "message", "level", "level_display", "read", "created_at"]
        read_only_fields = ["id", "created_at"]
