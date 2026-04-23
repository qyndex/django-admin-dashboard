"""Views for the dashboard frontend and authentication."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect, render

from .forms import RegistrationForm
from .models import (
    Activity,
    DashboardMetric,
    Department,
    Employee,
    Notification,
    Project,
)


def register_view(request):
    """User registration with auto-login on success."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect("dashboard:home")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard_home(request):
    """Main dashboard overview with real metrics, activity, and notifications."""
    # Key metrics
    metrics = DashboardMetric.objects.all()[:8]

    # Summary counts
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status=Employee.STATUS_ACTIVE).count()
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status=Project.STATUS_ACTIVE).count()
    total_departments = Department.objects.count()

    # Total budget across active projects
    total_budget = Project.objects.filter(status=Project.STATUS_ACTIVE).aggregate(
        total=Sum("budget")
    )["total"] or 0

    # Department breakdown for chart data
    dept_stats = (
        Department.objects.annotate(emp_count=Count("employees"))
        .values("name", "emp_count")
        .order_by("-emp_count")
    )

    # Project status breakdown
    project_stats = (
        Project.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    # Recent activity
    recent_activities = Activity.objects.select_related("user").all()[:10]

    # User notifications (unread first)
    user_notifications = Notification.objects.filter(user=request.user).order_by("read", "-created_at")[:5]
    unread_count = Notification.objects.filter(user=request.user, read=False).count()

    # Recent employees
    recent_employees = Employee.objects.select_related("user", "department").all()[:5]

    context = {
        "metrics": metrics,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_departments": total_departments,
        "total_budget": total_budget,
        "dept_stats": list(dept_stats),
        "project_stats": list(project_stats),
        "recent_activities": recent_activities,
        "notifications": user_notifications,
        "unread_count": unread_count,
        "recent_employees": recent_employees,
    }
    return render(request, "dashboard/home.html", context)


@login_required
def notifications_view(request):
    """List all notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(read=False).count()
    return render(request, "dashboard/notifications.html", {
        "notifications": notifications,
        "unread_count": unread_count,
    })


@login_required
def mark_notification_read(request, pk):
    """Mark a single notification as read."""
    Notification.objects.filter(pk=pk, user=request.user).update(read=True)
    return redirect("dashboard:notifications")


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user."""
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("dashboard:notifications")


@login_required
def activity_log_view(request):
    """Paginated activity log."""
    activities = Activity.objects.select_related("user").all()[:50]
    return render(request, "dashboard/activity_log.html", {"activities": activities})
