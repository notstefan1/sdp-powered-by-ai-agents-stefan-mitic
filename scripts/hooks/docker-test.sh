#!/usr/bin/env bash
set -e

# Skip if source files don't exist yet (pre-Module 5)
if [[ ! -f requirements.txt || ! -d src || ! -d tests ]]; then
  echo "⏭️  Skipping Docker test: src/, tests/, or requirements.txt not found yet."
  exit 0
fi

echo "🐳 Building Docker test image..."
docker build -t kata-tests .

echo "🧪 Running tests inside container..."
docker run --rm kata-tests
