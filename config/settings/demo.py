"""Demo / Coolify settings — SQLite, no SSL redirect, works with no external DB."""
import os

from .base import *  # noqa: F401, F403

DEBUG = False

# Allow any host — Coolify proxies via its own domain; set ALLOWED_HOSTS to
# restrict if desired.
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-demo-key-change-for-real-production-use"
)

# Use SQLite by default; override with individual DB_* vars or DATABASE_URL
# for PostgreSQL in environments where a real DB is available.
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url:
    # Minimal DATABASE_URL parsing (postgres://user:pass@host:port/dbname)
    import urllib.parse as _up

    _parsed = _up.urlparse(_db_url)
    DATABASES = {  # type: ignore[name-defined]  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _parsed.path.lstrip("/"),
            "USER": _parsed.username or "",
            "PASSWORD": _parsed.password or "",
            "HOST": _parsed.hostname or "localhost",
            "PORT": str(_parsed.port or 5432),
        }
    }
elif os.environ.get("DB_NAME"):
    DATABASES = {  # type: ignore[name-defined]  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    # Fall back to SQLite — zero config needed for the demo
    DATABASES = {  # type: ignore[name-defined]  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "/app/data/db.sqlite3",
        }
    }

# Static files served by WhiteNoise or gunicorn in demo mode
MIDDLEWARE = [  # type: ignore[name-defined]  # noqa: F405
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# No SSL redirect — Coolify handles TLS termination at the proxy layer
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Allow Coolify's proxy to set the proto header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
