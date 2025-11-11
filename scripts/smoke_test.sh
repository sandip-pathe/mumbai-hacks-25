#!/usr/bin/env bash
set -euo pipefail

BASE_URL=http://localhost:8080
RETRY=6
SLEEP=2

check() {
  local path="$1"
  local expected_code=${2:-200}
  local url="$BASE_URL$path"

  for i in $(seq 1 $RETRY); do
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)
    if [ "$code" = "$expected_code" ]; then
      echo "OK $path -> $code"
      return 0
    fi
    echo "Attempt $i/$RETRY: $path -> $code (expected $expected_code). Retrying in ${SLEEP}s..."
    sleep $SLEEP
  done

  echo "FAIL $path -> last_code=$code (expected $expected_code)"
  return 2
}

# Endpoints to check: root, API health, OpenAPI, docs
check "/" 200
check "/api/health" 200
check "/openapi.json" 200
check "/docs" 200

echo "SMOKE TEST PASSED"
