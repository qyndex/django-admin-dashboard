"""Production settings.

Note: For the Coolify demo deployment we pin DJANGO_SETTINGS_MODULE to
``config.settings.demo`` in ``docker-entrypoint.sh``. This module is kept
strict-by-design and should only load when a real Postgres database is wired
up — every required env var must be present.
"""
import os

from .base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# TLS is terminated at the upstream proxy (Traefik / Coolify). Trust the
# X-Forwarded-Proto header it sets and DO NOT issue a redirect from Django —
# that path leads to an infinite redirect loop behind the proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
