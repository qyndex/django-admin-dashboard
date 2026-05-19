"""Demo / Coolify settings — SQLite, WhiteNoise statics, works with no external DB."""
import os
import urllib.parse as _up

from .base import *  # noqa: F401, F403

DEBUG = False

# Allow any host — Coolify proxies via its own domain; set ALLOWED_HOSTS to
# restrict if desired.
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-demo-key-change-for-real-production-use"
)

# -- Database selection ------------------------------------------------------
# Priority:
#   1. DATABASE_URL with postgres:// scheme  → real Postgres
#   2. DB_NAME env vars                      → real Postgres
#   3. Anything else (incl. sqlite:// or unset) → SQLite at /app/data/db.sqlite3
_db_url = os.environ.get("DATABASE_URL", "")
_parsed = _up.urlparse(_db_url) if _db_url else None
_is_postgres_url = bool(_parsed and _parsed.scheme in {"postgres", "postgresql"})

if _is_postgres_url:
    assert _parsed is not None
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
    # SQLite fallback — zero config needed for the demo.
    # Covers DATABASE_URL=sqlite:///app.db and the unset case.
    DATABASES = {  # type: ignore[name-defined]  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "/app/data/db.sqlite3",
        }
    }

# -- Middleware --------------------------------------------------------------
# WhiteNoise must come right after SecurityMiddleware so it can serve static
# files in production without needing a separate webserver.
MIDDLEWARE = [  # type: ignore[name-defined]  # noqa: F405
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# WhiteNoise-managed static files (compressed + cache-busted hashes)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# No SSL redirect — Coolify (Traefik) handles TLS termination at the proxy
# layer; redirecting here would cause an infinite loop.
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Allow Coolify's proxy to set the proto header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF trust the proxied domain. Coolify deploys behind https://*.qyngent.com.
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "https://*.qyngent.com,https://*.demo.qyngent.com",
    ).split(",")
    if o.strip()
]
