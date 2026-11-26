#!/usr/bin/env bash
set -euo pipefail

base_url="${BANKPULSE_URL:-http://localhost:8080}"

echo "[1/2] Verificando Payments API"
curl -fsS "$base_url/health/payments" |
  grep -Eq '"status"[[:space:]]*:[[:space:]]*"UP"'

echo "[2/2] Verificando Audit API"
curl -fsS "$base_url/health/audit" |
  grep -Eq '"status"[[:space:]]*:[[:space:]]*"UP"'

echo "TECHNICAL SMOKE PASS"