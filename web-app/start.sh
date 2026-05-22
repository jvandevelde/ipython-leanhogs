#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Ensure a data directory exists if none is specified
if [ -z "${DATA_DIR:-}" ]; then
  mkdir -p ./data
fi

echo "Starting Lean Hogs..."
echo "  Data directory : ${DATA_DIR:-$(pwd)/data}"
echo "  App URL        : http://localhost:${PORT:-8080}"
echo ""

docker compose up --build

echo ""
echo "Shutting down..."
docker compose down
