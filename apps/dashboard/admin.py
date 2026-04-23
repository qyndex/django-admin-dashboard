"""Custom admin configuration for the admin dashboard."""
from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from .models import (
    Activity,
    DashboardMetric,
    Department,
    Employee,
    Notification,
    Project,
    UserProfile,
)


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 0
    fields = ["user", "job_title", "status", "hire_date"]
    readonly_fields = ["user"]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "head", "employee_count", "created_at"]
    search_fields = ["name", "code"]
    ordering = ["code"]
    inlines = [EmployeeInline]

    @admin.display(description="Employees")
    def employee_count(self, obj: Department) -> int:
        return obj.employees.count()

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(_emp_count=Count("employees"))


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["full_name", "job_title", "department", "status", "hire_date", "salary"]
    list_filter = ["status", "department"]
    search_fields = ["user__first_name", "user__last_name", "job_title"]
    list_editable = ["status"]
    ordering = ["user__last_name"]
    raw_id_fields = ["user", "department"]

    @admin.display(description="Name")
    def full_name(self, obj: Employee) -> str:
        return obj.user.get_full_name()


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "status", "budget", "start_date", "end_date", "member_count"]
    list_filter = ["status", "department"]
    search_fields = ["name", "description"]
    filter_horizontal = ["members"]
    ordering = ["-created_at"]

    @admin.display(description="Members")
    def member_count(self, obj: Project) -> int:
        return obj.members.count()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "department", "created_at"]
    list_filter = ["role", "department"]
    search_fields = ["user__first_name", "user__last_name", "user__username"]
    raw_id_fields = ["user", "department"]
    ordering = ["user__last_name"]


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ["name", "value", "change_percent", "period", "created_at"]
    list_filter = ["period"]
    search_fields = ["name"]
    ordering = ["-created_at"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "description_short", "ip_address", "created_at"]
    list_filter = ["action", "created_at"]
    search_fields = ["description", "user__first_name", "user__last_name"]
    raw_id_fields = ["user"]
    ordering = ["-created_at"]
    readonly_fields = ["user", "action", "description", "ip_address", "created_at"]

    @admin.display(description="Description")
    def description_short(self, obj: Activity) -> str:
        return obj.description[:80] + "..." if len(obj.description) > 80 else obj.description


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "level", "read", "created_at"]
    list_filter = ["level", "read", "created_at"]
    search_fields = ["title", "message", "user__first_name", "user__last_name"]
    raw_id_fields = ["user"]
    ordering = ["-created_at"]
    list_editable = ["read"]
