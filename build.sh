#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "==> Installing uv"
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "==> uv version"
uv --version

echo "==> Syncing dependencies (frozen, no dev)"
uv sync --frozen --no-dev

echo "==> Building Tailwind CSS"
uv run python manage.py tailwind build

echo "==> Collecting static files"
uv run python manage.py collectstatic --noinput

echo "==> Running migrations"
uv run python manage.py migrate --noinput

echo "==> Build complete"
