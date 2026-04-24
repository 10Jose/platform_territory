#!/bin/sh
set -e
export POSTGRES_HOST="${POSTGRES_HOST:-db-ingestion}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
python <<'PY'
import os, socket, time
host = os.environ.get("POSTGRES_HOST", "db-ingestion")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
for _ in range(90):
    try:
        socket.create_connection((host, port), timeout=2).close()
        print("PostgreSQL is accepting connections.")
        raise SystemExit(0)
    except OSError:
        time.sleep(1)
print("Timeout waiting for PostgreSQL")
raise SystemExit(1)
PY
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
