#!/usr/bin/env python3
"""Disponibilidad tecnica solamente; no certifica resultados de negocio."""
import json
import os
from pathlib import Path
import sys
from urllib.request import urlopen


def main():
    base = os.environ.get("BANKPULSE_URL", "http://localhost:8080").rstrip("/")
    checks = []
    for path in ("/health/payments", "/health/audit", "/api/payments", "/api/audit"):
        check = {"path": path, "pass": False}
        try:
            with urlopen(base + path, timeout=15) as response:
                body = json.load(response)
                check["http_status"] = response.status
                check["pass"] = response.status == 200
                if path.startswith("/health/"):
                    check["status"] = body.get("status")
                    check["pass"] &= check["status"] == "UP"
                else:
                    check["pass"] &= isinstance(body, list)
        except Exception as error:
            check["error"] = str(error)
        checks.append(check)
    passed = all(check["pass"] for check in checks)
    report = {"result": "PASS" if passed else "BLOCK", "checks": checks}
    target = Path(os.environ.get("EVIDENCE_DIR", "evidence"))
    target.mkdir(parents=True, exist_ok=True)
    (target / "technical-smoke.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
