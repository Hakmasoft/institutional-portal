# Institutional Portal

A Django PWA for tertiary institutions to manage students, staff, attendance,
grades, and examination results.

See `docs/context/overview.md` for the full project brief.

## Local setup (requires [uv](https://docs.astral.sh/uv/))

1. `uv sync`
2. `cp .env.example .env` (Windows PowerShell: `Copy-Item .env.example .env`)
3. Set a real `DJANGO_SECRET_KEY` in `.env`
4. `uv run python manage.py migrate`
5. `uv run python manage.py runserver`

Health check: `http://127.0.0.1:8000/health/` -> `{"status": "ok"}`

Admin: `http://127.0.0.1:8000/admin/`

## Common commands

| Action | Command |
|--------|---------|
| Install/sync deps | `uv sync` |
| Add a dependency | `uv add <package>` |
| Add a dev dependency | `uv add --dev <package>` |
| Run a Django command | `uv run python manage.py <cmd>` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Update lockfile after manual edit | `uv lock` |

## Task progress

- [x] Task 1 - Project scaffolding (uv)
- [ ] Task 2 - Render deployment
- [ ] Task 3 - Academic structure models

## Deployment (Render)

Create a Render Blueprint from this repository and apply `render.yaml`. Render
creates the web service and Postgres database, generates the Django secret,
and provides `DATABASE_URL` automatically.

- Blueprint setup: select "New > Blueprint" in Render and connect this repository.
- Deploys: `autoDeploy` is enabled for pushes to `main`.
- Superuser: open the Render web-service Shell after deployment and run
  `uv run python manage.py createsuperuser`.
- Free-tier caveat: the web service sleeps after 15 minutes of inactivity.
- Free Postgres caveat: free databases expire after 90 days.
- HSTS follow-up: after confirming HTTPS deployment, set
  `DJANGO_SECURE_HSTS_SECONDS` to an intentional positive value and redeploy.