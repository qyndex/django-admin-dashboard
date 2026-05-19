FROM python:3.13-slim AS base
WORKDIR /app
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
RUN mkdir -p /app/data

# collectstatic runs at build time with the demo settings (SQLite, no DB needed)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Entrypoint: migrate then seed (idempotent) then serve
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_data 2>/dev/null || true && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"]
