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

## Logging in

Anonymous visitors to `/` are redirected to `/accounts/login/`. After
login, users are routed to their role-specific home:

| Role | Home |
|------|------|
| `student` | `/student/` (my courses) |
| `lecturer` / `hod` / `dean` | `/lecturer/` (my coordinated courses) |
| `admin` / superuser | `/admin/` (Django admin) |
| `registrar`, `finance`, `parent` | generic welcome page (placeholder) |

### Lecturer workflow (in progress)

- `/lecturer/` — grid of coordinated offerings
- `/lecturer/offerings/<id>/` — offering detail: course info, recent
  sessions, enrolled students roster, "Take attendance" action
- `/lecturer/offerings/<id>/attendance/today/` — attendance marking UI:
  sticky header with session context and live summary, one row per
  enrolled student with four status toggles (present/absent/late/excused),
  sticky footer with "mark all present" / "mark all absent" bulk actions
  and a Save button
- `/lecturer/offerings/<id>/attendance/today/save/` — POST endpoint that
  upserts AttendanceRecords for today's session and flips the session
  status from SCHEDULED to HELD

Object-level authorization: the coordinator of the offering, the HOD of
its department, the Dean of its faculty, and superusers can all view.
Other lecturers see 403.

Demo credentials (after `seed_demo`):

- Lecturer: `lecturer1` / `demo1234!`
- Student: `2023_mb_001` / `demo1234!`
- HOD: `hod_anat` / `demo1234!`
- Superuser: whichever you created via `createsuperuser`

## Design system

The UI is built on Tailwind CSS v4 (via `django-tailwind-cli`) and
`django-cotton` for component abstraction. See
[`docs/design.md`](docs/design.md) for tokens, components,
accessibility commitments, and development workflow.

### Frontend workflow

- **Dev:** `python manage.py tailwind runserver`
- **Or separate:** `python manage.py tailwind watch` + `runserver`
- **Production:** `python manage.py tailwind build` then `collectstatic`
- **After changing Tailwind classes or `assets/css/source.css`:** rebuild
  via the watcher or `tailwind build`

## Demo data

This is a portal for a medical tertiary institution. For local
development, populate a realistic dataset:

    uv run python manage.py seed_demo

This creates:
- 2 faculties (Medicine, Nursing), 4 departments
- 2 programmes (MBChB — Medicine & Surgery, BSN — Nursing)
- 1 academic year with 1 current term
- 4 courses (Anatomy, Physiology, Clinical Medicine, Nursing) with
  course offerings
- 2 staff (1 lecturer in Physiology, 1 HOD in Anatomy)
- 10 students across the two programmes, enrolled across the offerings

All demo users share the password `demo1234!`. Log in as:
- `lecturer1` (lecturer, coordinates PHYS101 Medical Physiology I)
- `hod_anat` (HOD, Anatomy)
- `2023_mb_001` … `2024_bn_002` (medical and nursing students)

Re-running `seed_demo` is idempotent (uses get_or_create throughout).

To start fresh:

    uv run python manage.py flush --no-input
    uv run python manage.py seed_demo

`seed_demo` refuses to run when `DEBUG=False` — it will raise
`CommandError` to prevent accidental seeding of production databases.