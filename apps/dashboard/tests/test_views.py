"""Tests for dashboard frontend views and authentication."""
import pytest
from django.contrib.auth.models import User
from django.test import Client

from apps.dashboard.factories import (
    ActivityFactory,
    DashboardMetricFactory,
    NotificationFactory,
)


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def logged_in_client(client: Client, admin_user) -> Client:
    client.force_login(admin_user)
    return client


@pytest.mark.django_db
class TestDashboardHomeView:
    def test_redirects_anonymous_to_login(self, client: Client) -> None:
        res = client.get("/")
        assert res.status_code == 302
        assert "/accounts/login/" in res.url

    def test_renders_for_authenticated_user(self, logged_in_client: Client) -> None:
        res = logged_in_client.get("/")
        assert res.status_code == 200
        assert b"Dashboard" in res.content

    def test_shows_metrics(self, logged_in_client: Client) -> None:
        DashboardMetricFactory(name="Revenue", value=5000)
        res = logged_in_client.get("/")
        assert res.status_code == 200
        assert b"Revenue" in res.content

    def test_shows_recent_activities(self, logged_in_client: Client, admin_user) -> None:
        ActivityFactory(user=admin_user, description="Did something important")
        res = logged_in_client.get("/")
        assert res.status_code == 200
        assert b"Did something important" in res.content

    def test_shows_notifications(self, logged_in_client: Client, admin_user) -> None:
        NotificationFactory(user=admin_user, title="Test Alert")
        res = logged_in_client.get("/")
        assert res.status_code == 200
        assert b"Test Alert" in res.content


@pytest.mark.django_db
class TestNotificationsView:
    def test_redirects_anonymous(self, client: Client) -> None:
        res = client.get("/notifications/")
        assert res.status_code == 302

    def test_renders_notifications(self, logged_in_client: Client, admin_user) -> None:
        NotificationFactory(user=admin_user, title="Alert One")
        NotificationFactory(user=admin_user, title="Alert Two")
        res = logged_in_client.get("/notifications/")
        assert res.status_code == 200
        assert b"Alert One" in res.content
        assert b"Alert Two" in res.content

    def test_mark_notification_read(self, logged_in_client: Client, admin_user) -> None:
        notif = NotificationFactory(user=admin_user, read=False)
        res = logged_in_client.get(f"/notifications/{notif.pk}/read/")
        assert res.status_code == 302
        notif.refresh_from_db()
        assert notif.read is True

    def test_mark_all_read(self, logged_in_client: Client, admin_user) -> None:
        NotificationFactory.create_batch(3, user=admin_user, read=False)
        res = logged_in_client.get("/notifications/read-all/")
        assert res.status_code == 302
        from apps.dashboard.models import Notification
        assert Notification.objects.filter(user=admin_user, read=False).count() == 0


@pytest.mark.django_db
class TestActivityLogView:
    def test_redirects_anonymous(self, client: Client) -> None:
        res = client.get("/activity/")
        assert res.status_code == 302

    def test_renders_activity_log(self, logged_in_client: Client, admin_user) -> None:
        ActivityFactory(user=admin_user, description="Logged in")
        res = logged_in_client.get("/activity/")
        assert res.status_code == 200
        assert b"Logged in" in res.content


@pytest.mark.django_db
class TestRegistrationView:
    def test_renders_registration_form(self, client: Client) -> None:
        res = client.get("/accounts/register/")
        assert res.status_code == 200
        assert b"Create Account" in res.content

    def test_successful_registration_redirects(self, client: Client) -> None:
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password1": "Str0ngP@ss!",
            "password2": "Str0ngP@ss!",
        }
        res = client.post("/accounts/register/", payload)
        assert res.status_code == 302
        assert User.objects.filter(username="newuser").exists()

    def test_registration_logs_in_user(self, client: Client) -> None:
        payload = {
            "username": "autouser",
            "email": "auto@example.com",
            "first_name": "Auto",
            "last_name": "Login",
            "password1": "Str0ngP@ss!",
            "password2": "Str0ngP@ss!",
        }
        res = client.post("/accounts/register/", payload, follow=True)
        assert res.status_code == 200
        # Should be on the dashboard (logged in)
        assert b"Dashboard" in res.content

    def test_invalid_registration_shows_errors(self, client: Client) -> None:
        payload = {
            "username": "",
            "email": "bad",
            "first_name": "",
            "last_name": "",
            "password1": "short",
            "password2": "mismatch",
        }
        res = client.post("/accounts/register/", payload)
        assert res.status_code == 200  # re-renders form


@pytest.mark.django_db
class TestLoginView:
    def test_renders_login_form(self, client: Client) -> None:
        res = client.get("/accounts/login/")
        assert res.status_code == 200
        assert b"Sign In" in res.content

    def test_successful_login_redirects_to_dashboard(self, client: Client, admin_user) -> None:
        res = client.post("/accounts/login/", {"username": "admin", "password": "adminpass123"}, follow=True)
        assert res.status_code == 200
        assert b"Dashboard" in res.content

    def test_invalid_login_shows_error(self, client: Client) -> None:
        res = client.post("/accounts/login/", {"username": "bad", "password": "bad"})
        assert res.status_code == 200
        assert b"Invalid" in res.content or b"username" in res.content
