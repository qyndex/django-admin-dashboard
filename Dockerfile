FROM python:3.13-slim AS base
WORKDIR /app

# DJANGO_SETTINGS_MODULE intentionally pinned here AND re-forced in
# docker-entrypoint.sh — Coolify env injection can otherwise flip this to
# config.settings.prod and crash the import on missing DB_NAME.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.demo

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Persistent SQLite lives here; mount a volume at /app/data in production
# (Coolify: add a Persistent Storage entry on /app/data to survive redeploys).
RUN mkdir -p /app/data /app/staticfiles

# collectstatic runs at build time with the demo settings (SQLite, no DB
# needed). WhiteNoise's compressed-manifest backend writes hashed assets to
# /app/staticfiles so they survive container restarts.
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Entrypoint forces demo settings, migrates, seeds (non-fatal), then execs
# gunicorn --preload so import errors surface immediately.
RUN chmod +x /app/docker-entrypoint.sh
CMD ["/app/docker-entrypoint.sh"]
