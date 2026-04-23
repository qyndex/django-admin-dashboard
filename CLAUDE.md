# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django Admin Dashboard -- a full-featured company administration dashboard with real authentication, database-backed metrics, activity logging, and notification system. Built on top of Django's admin framework with a custom frontend and REST API.

Built with Django 5.x, Python 3.13, Django REST Framework, and SQLite (dev) / PostgreSQL (prod).

## Quick Start

```bash
# 1. Create virtual environment and install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Copy environment config
cp .env.example .env

# 3. Run migrations
python manage.py migrate

# 4. Seed demo data (creates admin/admin user + realistic sample data)
python manage.py seed_data

# 5. Start dev server
python manage.py runserver
# Dashboard: http://localhost:8000/
# Admin:     http://localhost:8000/admin/
# API:       http://localhost:8000/api/
```

**Demo credentials**: `admin` / `admin` (superuser), or any seeded employee username / `demo1234`

## Commands

```bash
# Development
python manage.py runserver               # Start dev server (http://localhost:8000)
python manage.py seed_data               # Populate demo data (departments, employees, projects, metrics)
python manage.py seed_data --clear       # Clear existing data and reseed
python manage.py createsuperuser         # Create admin user manually

# Database
python manage.py makemigrations          # Create new migrations after model changes
python manage.py migrate                 # Apply migrations

# Testing
python -m pytest -v --tb=short           # Run all tests
python -m pytest apps/dashboard/tests/test_models.py -v  # Run specific test file
python -m pytest -k "test_employee" -v   # Run tests matching pattern

# Code quality
ruff check .                             # Lint
ruff format .                            # Format
mypy .                                   # Type check (optional)
```

## Architecture

```
config/
  settings/
    base.py          -- Shared settings (installed apps, middleware, DRF config)
    dev.py           -- Development settings (SQLite, DEBUG=True)
    prod.py          -- Production settings (PostgreSQL, security hardening)
  urls.py            -- Root URL routing (dashboard + auth + admin + API)
  wsgi.py            -- WSGI entry point

apps/dashboard/
  models.py          -- All models: Department, Employee, Project, UserProfile,
                        DashboardMetric, Activity, Notification
  admin.py           -- ModelAdmin classes with list displays, filters, inlines
  views.py           -- Dashboard frontend views (home, notifications, activity log)
  viewsets.py        -- DRF ViewSets for all models (CRUD + custom actions)
  serializers.py     -- DRF serializers with computed fields
  forms.py           -- Registration form extending UserCreationForm
  urls.py            -- Dashboard view URLs + API router
  factories.py       -- Factory Boy factories for all models (used in tests)
  management/
    commands/
      seed_data.py   -- Management command to populate realistic demo data

templates/
  base.html          -- Root HTML template
  base_auth.html     -- Auth page layout (login, register)
  base_dashboard.html-- Dashboard layout with sidebar, topbar, navigation
  registration/
    login.html       -- Login page
    register.html    -- Registration page
    logged_out.html  -- Post-logout page
  dashboard/
    home.html        -- Main dashboard with metrics, activity, notifications
    notifications.html -- Notification center with mark-read actions
    activity_log.html  -- Full activity log table

static/css/
  style.css          -- Complete dashboard styling (no external CSS dependencies)
```

## Models

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `Department` | Organisational units | name, code, head (FK User) |
| `Employee` | Staff records linked to Users | user (1:1), department, job_title, salary, status, hire_date |
| `Project` | Business projects with teams | name, department, status, budget, members (M2M Employee) |
| `UserProfile` | Extended user data | user (1:1), avatar, role, department |
| `DashboardMetric` | KPI display cards | name, value, change_percent, period |
| `Activity` | Audit trail | user, action, description, ip_address |
| `Notification` | User alerts with read tracking | user, title, message, level, read |

## API Endpoints

All endpoints require authentication (session or basic auth).

| Prefix | ViewSet | Custom Actions |
|--------|---------|----------------|
| `/api/departments/` | DepartmentViewSet | -- |
| `/api/employees/` | EmployeeViewSet | `by-department/{id}/` |
| `/api/projects/` | ProjectViewSet | `active/` |
| `/api/metrics/` | DashboardMetricViewSet | `by-period/{period}/` |
| `/api/activities/` | ActivityViewSet (read-only) | `by-user/{id}/` |
| `/api/notifications/` | NotificationViewSet | `mark-read/`, `mark-all-read/`, `unread-count/` |

## URL Routes

| Path | View | Purpose |
|------|------|---------|
| `/` | `dashboard_home` | Main dashboard (login required) |
| `/notifications/` | `notifications_view` | Notification center |
| `/activity/` | `activity_log_view` | Activity log |
| `/accounts/login/` | Django auth | Login |
| `/accounts/logout/` | Django auth | Logout |
| `/accounts/register/` | `register_view` | User registration |
| `/admin/` | Django admin | Admin panel |
| `/api/` | DRF router | API root |

## Rules

- Always create migrations for model changes: `python manage.py makemigrations`
- Use class-based views for CRUD, function views for simple endpoints
- Parameterized queries only -- never raw SQL with string interpolation
- All new models need proper `__str__` and `Meta.ordering`
- All new DRF endpoints need corresponding serializers and viewset tests
- Factory Boy factories must be updated when adding new models
- Login is required for all dashboard views and API endpoints
- Use `select_related` / `prefetch_related` in querysets to avoid N+1 queries
- Templates extend `base_dashboard.html` for logged-in pages, `base_auth.html` for auth pages
