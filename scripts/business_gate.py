#!/usr/bin/env python3
"""Prueba de negocio contra las APIs reales y MariaDB; sin dependencias pip."""
from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4


def request(base, path, payload=None, key=None):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["X-Idempotency-Key"] = key
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(base + path, data=data, headers=headers)
    try:
        with urlopen(req, timeout=15) as response:
            return {"http_status": response.status, "body": json.load(response)}
    except HTTPError as error:
        return {"http_status": error.code, "body": error.read().decode()}


def ledger(account):
    # account solo contiene el prefijo fijo y un UUID generado por esta prueba.
    query = (
        "SELECT COUNT(*), COALESCE(SUM(amount),0) "
        f"FROM payments WHERE account='{account}';"
    )
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", "mariadb", "sh", "-c",
         'exec mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" '
         '"$MARIADB_DATABASE" --batch --skip-column-names -e "$1"',
         "sh", query],
        capture_output=True, text=True, timeout=30, check=True,
    )
    count, total = result.stdout.strip().split("\t")
    return {"payment_count": int(count), "total_usd": str(Decimal(total))}


def main():
    base = os.environ.get("BANKPULSE_URL", "http://localhost:8080").rstrip("/")
    token = uuid4().hex
    account = "gate-" + token
    key = "gate-" + token
    payload = {"account": account, "amount": 500.00, "currency": "USD"}
    report = {
        "capacity": "Procesar el mismo pago una sola vez",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "account": account,
        "idempotency_key": key,
        "request": payload,
        "expected": {"requests": 2, "payment_count": 1, "total_usd": "500.00", "audit_count": 1},
        "checks": [],
        "result": "BLOCK",
    }

    def check(name, condition, actual):
        report["checks"].append({"name": name, "pass": bool(condition), "actual": actual})

    try:
        responses = [request(base, "/api/payments", payload, key) for _ in range(2)]
        report["responses"] = responses
        check("ambas solicitudes responden HTTP 200",
              all(r["http_status"] == 200 for r in responses),
              [r["http_status"] for r in responses])
        if any(not isinstance(r["body"], dict) for r in responses):
            raise ValueError("El endpoint no devolvio objetos de pago")
        bodies = [r["body"] for r in responses]
        ids = [body.get("id") for body in bodies]
        check("mismo identificador no vacio", bool(ids[0]) and ids[0] == ids[1], ids)
        for index, body in enumerate(bodies, 1):
            check(f"respuesta {index} conserva la orden",
                  body.get("account") == account
                  and body.get("idempotencyKey") == key
                  and Decimal(str(body.get("amount", 0))) == Decimal("500.00")
                  and body.get("currency") == "USD"
                  and body.get("status") == "ACCEPTED", body)

        # Evidencia persistida: devolver dos IDs iguales no basta para pasar.
        persisted = ledger(account)
        report["ledger"] = persisted
        check("MariaDB contiene exactamente un pago", persisted["payment_count"] == 1, persisted["payment_count"])
        check("importe total registrado USD 500.00",
              Decimal(persisted["total_usd"]) == Decimal("500.00"), persisted["total_usd"])
        report["excess_registered_usd"] = str(max(Decimal("0"), Decimal(persisted["total_usd"]) - Decimal("500.00")))

        # El evento debe ser de esta operacion; no sirve un PAYMENT_CREATED antiguo.
        deadline = time.monotonic() + 30
        matching = []
        while True:
            audit = request(base, "/api/audit")
            if audit["http_status"] != 200 or not isinstance(audit["body"], list):
                raise ValueError("No se pudo consultar la auditoria")
            matching = [e for e in audit["body"] if e.get("payload", {}).get("account") == account]
            if len(matching) >= persisted["payment_count"] or time.monotonic() >= deadline:
                break
            time.sleep(1)
        report["audit_events"] = matching
        check("exactamente un evento para este pago", len(matching) == 1, len(matching))
        check("auditoria conserva ID, importe y moneda",
              len(matching) == 1
              and matching[0].get("aggregateId") == ids[0]
              and matching[0].get("eventType") == "PAYMENT_CREATED"
              and Decimal(str(matching[0].get("payload", {}).get("amount", 0))) == Decimal("500.00")
              and matching[0].get("payload", {}).get("currency") == "USD",
              matching)
        health = {path: request(base, path) for path in ("/health/payments", "/health/audit")}
        report["health_after_requests"] = health
        check("infraestructura sigue UP despues de los pagos",
              all(r["http_status"] == 200 and r["body"].get("status") == "UP" for r in health.values()), health)
        if all(item["pass"] for item in report["checks"]):
            report["result"] = "PASS"
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    finally:
        destination = Path(os.environ.get("EVIDENCE_DIR", "evidence"))
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "business-gate.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        print("RELEASE PASS" if report["result"] == "PASS" else "RELEASE BLOCKED")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
