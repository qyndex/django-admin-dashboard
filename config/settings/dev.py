"""Development settings."""
import os

from .base import *  # noqa: F401, F403

DEBUG = os.environ.get("DEBUG", "true").lower() != "false"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DB_PATH", str(BASE_DIR / "db.sqlite3")),  # noqa: F405
    }
}

INSTALLED_APPS += ["django_extensions"]  # noqa: F405

# Email backend for development — print to console instead of sending
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
