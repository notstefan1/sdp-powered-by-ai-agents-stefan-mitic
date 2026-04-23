#!/usr/bin/env bash
set -e

if [[ ! -f requirements.txt || ! -d src || ! -d tests ]]; then
  echo "⏭️  Skipping Docker test: src/, tests/, or requirements.txt not found yet."
  exit 0
fi

echo "🐳 Building Docker test image..."
docker build -t kata-tests .

echo "🧪 Running unit tests (no infrastructure)..."
docker run --rm -e TESTING=1 kata-tests pytest tests/ -v --tb=short

echo "🧪 Running integration tests (with postgres + redis)..."
docker compose --profile test up --build --abort-on-container-exit --exit-code-from test test
docker compose --profile test down -v
