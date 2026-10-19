#!/usr/bin/env python3
"""Inyectar o revertir una regresion concreta en una rama de laboratorio."""
import argparse
from pathlib import Path
import subprocess

SOURCE = Path(__file__).resolve().parents[1] / "services/payments-api/src/main/java/com/bankpulse/payments/PaymentService.java"
CORRECT = "return payments.findByIdempotencyKey(idempotencyKey).orElseGet(() -> persist(idempotencyKey, request));"
BROKEN = "return persist(UUID.randomUUID().toString(), request); // FALSO VERDE: pierde la clave original"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inject", "restore"))
    args = parser.parse_args()
    if args.action == "inject":
        branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=SOURCE.parents[8], text=True).strip()
        if branch in ("", "main", "master"):
            parser.error("Crea primero una rama de laboratorio: git switch -c demo/falso-verde-local")
    old, new = (CORRECT, BROKEN) if args.action == "inject" else (BROKEN, CORRECT)
    content = SOURCE.read_text()
    if content.count(old) != 1:
        parser.error("No se encontro exactamente la linea esperada; no se modifico ningun archivo")
    SOURCE.write_text(content.replace(old, new))
    print("Falla inyectada" if args.action == "inject" else "Idempotencia restaurada")
    print("Reconstruye: docker compose up -d --build --wait --wait-timeout 360 payments-api console")


if __name__ == "__main__":
    main()
