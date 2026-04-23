"""Custom admin configuration for the admin dashboard."""
from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from .models import Department, Employee, Project


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
