#!/usr/bin/env sh
set -eu

echo "[start] Running migrations and schema sync check..."
python -m app.scripts.migrate_and_check

echo "[start] Running admin bootstrap script..."
python -m app.scripts.bootstrap_admin

echo "[start] Running prompt template bootstrap script..."
python -m app.scripts.bootstrap_prompt_template

echo "[start] Ensuring Ollama model is available..."
python -m app.scripts.ensure_ollama_model

if [ "$#" -eq 0 ]; then
	set -- python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8001}"
fi

echo "[start] Starting: $*"
exec "$@"