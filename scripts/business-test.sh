  #!/usr/bin/env bash
set -euo pipefail

base_url="${BANKPULSE_URL:-http://localhost:8080}"
payment_key="business-$(date +%s)-${RANDOM}"
payment_account="$payment_key"

echo "[1/4] Verificando APIs"
curl -fsS "$base_url/health/payments" >/dev/null
curl -fsS "$base_url/health/audit" >/dev/null

echo "[2/4] Creando pago idempotente"
curl -fsS -X POST "$base_url/api/payments" \
  -H 'Content-Type: application/json' \
  -H "X-Idempotency-Key: $payment_key" \
  -d "{\"account\":\"$payment_account\",\"amount\":500.00,\"currency\":\"USD\"}" >/tmp/bankpulse-payment.json

echo "[3/4] Reintentando la misma solicitud"
curl -fsS -X POST "$base_url/api/payments" \
  -H 'Content-Type: application/json' \
  -H "X-Idempotency-Key: $payment_key" \
  -d "{\"account\":\"$payment_account\",\"amount\":500.00,\"currency\":\"USD\"}" >/tmp/bankpulse-payment-retry.json
first_id="$(sed -n 's/.*"id":"\([^"]*\)".*/\1/p' /tmp/bankpulse-payment.json)"
retry_id="$(sed -n 's/.*"id":"\([^"]*\)".*/\1/p' /tmp/bankpulse-payment-retry.json)"

echo "[Negocio] Consultando los pagos registrados en MariaDB"

db_result="$(docker compose exec -T mariadb sh -c \
  'mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" \
  "$MARIADB_DATABASE" --batch --skip-column-names -e "$1"' \
  sh "SELECT COUNT(*), COALESCE(SUM(amount), 0)
      FROM payments
      WHERE account='$payment_account';")"

read -r payment_count payment_total <<< "$db_result"

echo "Esperado: 1 pago por USD 500.00"
echo "Observado: $payment_count pagos por USD $payment_total"

if [[ "$payment_count" != "1" || "$payment_total" != "500.00" ]]; then
  echo "RELEASE BLOCKED: el pago no se registro una sola vez"
  exit 1
fi

[ -n "$first_id" ]
[ "$first_id" = "$retry_id" ]

echo "[4/4] Esperando publicación del outbox"
for _ in $(seq 1 20); do
  pending="$(curl -fsS "$base_url/api/outbox" | sed -n 's/.*"pending":\([0-9]*\).*/\1/p')"
  [ "$pending" = "0" ] && break
  sleep 1
done
[ "${pending:-1}" = "0" ]
curl -fsS "$base_url/api/audit" | grep -q 'PAYMENT_CREATED'
echo "BUSINESS TEST PASS"
