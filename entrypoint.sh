#!/usr/bin/env sh
set -eu

echo "[start] Running Alembic migrations..."
echo "[start] Checking Alembic schema sync..."

echo "[start] Checking Alembic schema sync..."
if ! python -m alembic revision --autogenerate --check > /dev/null 2>&1; then
	echo "[info] Alembic schema is out of sync. Generating migration..."
	python -m alembic revision --autogenerate -m "auto sync migration"
	echo "[info] Applying new migration..."
	python -m alembic upgrade head
else
	python -m alembic upgrade head
fi

echo "[start] Running admin bootstrap script..."
python -m app.scripts.bootstrap_admin

if [ "$#" -eq 0 ]; then
	set -- python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
fi

echo "[start] Starting: $*"
exec "$@"