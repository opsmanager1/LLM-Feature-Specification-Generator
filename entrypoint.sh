#!/usr/bin/env sh
set -eu

echo "[start] Running Alembic migrations..."
python -m alembic upgrade head

echo "[start] Checking Alembic schema sync..."
python -m alembic check || {
	echo "[error] Alembic schema is out of sync! Create and commit migrations before deploy." >&2
	exit 1
}

echo "[start] Running admin bootstrap script..."
python -m app.scripts.bootstrap_admin

if [ "$#" -eq 0 ]; then
	set -- python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
fi

echo "[start] Starting: $*"
exec "$@"