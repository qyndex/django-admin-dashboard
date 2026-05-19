# Django Admin Dashboard
Custom Django admin dashboard with departments, employees, and projects — custom ModelAdmin classes, inline editing, DRF viewsets, and annotated querysets.

## Stack

- **Framework:** Django
- **Language:** Python
- **Database:** Django ORM (Postgres in prod, SQLite in dev)
- **Auth:** Django auth (django.contrib.auth)
- **Styling:** Django templates + static CSS

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env  # then edit and fill in the keys below

# 3. Apply database migrations
python manage.py migrate

# 4. Start the dev server
python manage.py runserver

# Run tests
pytest
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | no | Python path of the active Django settings module. |
| `DJANGO_SECRET_KEY` | yes | Django SECRET_KEY — must be unique per deployment. |
| `DEBUG` | no | (no description — see .env.example) |
| `ALLOWED_HOSTS` | no | (no description — see .env.example) |
| `DB_PATH` | no | (no description — see .env.example) |

## Project structure (top 2 levels)

```
apps/
  dashboard/
  __init__.py
config/
  settings/
  __init__.py
  urls.py
  wsgi.py
static/
  css/
  js/
templates/
  dashboard/
  registration/
  base.html
  base_auth.html
  base_dashboard.html
CLAUDE.md
CONTRIBUTING.md
Dockerfile
LICENSE
README.md
conftest.py
docker-compose.yml
manage.py
mypy.ini
pytest.ini
requirements.txt
ruff.toml
```

## Routes / pages

- `/`
- `/accounts`
- `/accounts/register`
- `/admin`
- `/api`
- `/dashboard`
- `/dashboard/notifications`
- `/dashboard/notifications/<int:pk>/read`
- `/dashboard/notifications/read-all`
- `/dashboard/activity`

## Tests

- Unit / integration: `pytest`

## Deploy

This template ships a `Dockerfile` and `docker-compose.yml`. For local end-to-end runs use `docker compose up --build`; for image-based deploys build with `docker build -t <name> .` and ship to your registry.

## Customising for your build

When you ask Qyngent to build on top of this template, mention:

- **Brand & product name** — replace any placeholder copy in this template.
- **Color scheme & typography** — drives Tailwind tokens / theme files.
- **Features beyond the baseline** — this template already ships:
  - Django auth (django.contrib.auth)
  - 10 route(s) / screen(s)
- **Integrations** — list any third-party APIs you want wired in.
- **Deployment target** — Qyngent defaults to its hosted platform; tell us if you need a specific cloud.

Built with [Qyngent](https://qyngent.com) — autonomous app generation that uses this template as a starting point.
