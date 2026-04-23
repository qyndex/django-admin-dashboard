"""Pytest configuration and shared fixtures for the admin dashboard project."""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Unauthenticated DRF test client."""
    return APIClient()


@pytest.fixture
def admin_user(db) -> User:
    """Superuser with full admin access."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def regular_user(db) -> User:
    """Regular (non-staff) user."""
    return User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="regularpass123",
        first_name="Regular",
        last_name="User",
    )


@pytest.fixture
def authed_client(api_client: APIClient, admin_user: User) -> APIClient:
    """DRF client authenticated as the admin superuser."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def user_client(api_client: APIClient, regular_user: User) -> APIClient:
    """DRF client authenticated as a regular user."""
    api_client.force_authenticate(user=regular_user)
    return api_client
