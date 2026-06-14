#!/usr/bin/env bash
# Start the API server.
export PGUSER="${PGUSER:-postgres}"
export PGDATABASE="${PGDATABASE:-finance}"
exec uvicorn app.main:app --host 0.0.0.0 --port 4000
