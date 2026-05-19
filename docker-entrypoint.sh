#!/bin/sh
# Coolify-resilient entrypoint for the Django admin dashboard demo.
#
# 1. FORCE the demo settings module regardless of what Coolify injects via env.
#    Coolify currently ships DJANGO_SETTINGS_MODULE=config.settings.prod which
#    requires DB_NAME/DB_USER/DB_PASSWORD env vars that aren't set, so prod
#    crashes on import. We hard-pin demo here.
# 2. Run migrations (required — SQLite has no schema until migrate runs).
# 3. Seed demo data, but never let a seeding failure prevent gunicorn from
#    serving traffic.
# 4. Exec gunicorn with --preload so import-time errors surface immediately
#    and all workers share the loaded Django app.
set -e

export DJANGO_SETTINGS_MODULE=config.settings.demo

mkdir -p /app/data

echo "[entrypoint] running migrations..."
python manage.py migrate --noinput

echo "[entrypoint] seeding demo data (idempotent, failures are non-fatal)..."
python manage.py seed_data 2>&1 || echo "[entrypoint] seed_data failed — continuing"

echo "[entrypoint] starting gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 60 \
    --preload \
    --access-logfile - \
    --error-logfile -
