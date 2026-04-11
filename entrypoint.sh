#!/usr/bin/env sh
set -eu

echo "[start] Running Alembic migrations..."
python -m alembic upgrade head

echo "[start] Running admin bootstrap script..."
python -m app.scripts.bootstrap_admin

if [ "$#" -eq 0 ]; then
	set -- python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
fi

echo "[start] Starting: $*"
exec "$@"