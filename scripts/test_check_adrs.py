import tempfile
import unittest
from pathlib import Path
from check_adrs import change_policy, validate

VALID = """# 1. Ejemplo

Date: 2026-11-25

## Status

Accepted

## Context

Los reintentos pueden duplicar un pago.

## Decision

Reutilizar la clave de idempotencia.

## Consequences

Una misma solicitud conserva su identificador.
"""


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.record = self.directory / "0001-ejemplo.md"
        self.record.write_text(VALID, encoding="utf-8")

    def test_complete_record_passes(self):
        self.assertEqual(validate(self.directory), [])

    def test_empty_decision_fails(self):
        self.record.write_text(VALID.replace("Reutilizar la clave de idempotencia.", ""))
        self.assertTrue(any("empty Decision" in e for e in validate(self.directory)))

    def test_broken_evidence_link_fails(self):
        self.record.write_text(VALID + "\n[Evidencia](../../missing.java)\n")
        self.assertTrue(any("broken local link" in e for e in validate(self.directory)))

    def test_default_template_fails(self):
        self.record.write_text(VALID.replace("Los reintentos pueden duplicar un pago.", "Completar contexto"))
        self.assertTrue(any("unfilled template" in e for e in validate(self.directory)))

    def test_duplicate_number_fails(self):
        (self.directory / "0001-otro.md").write_text(VALID)
        self.assertTrue(any("duplicate" in e for e in validate(self.directory)))

    def test_invalid_calendar_date_fails(self):
        self.record.write_text(VALID.replace("2026-11-25", "2026-02-30"))
        self.assertTrue(any("valid ISO Date" in e for e in validate(self.directory)))

    def test_superseded_record_requires_replacement(self):
        self.record.write_text(VALID.replace("Accepted", "Superceded by"))
        self.assertTrue(any("replacement ADR link" in e for e in validate(self.directory)))

    def test_upstream_replacement_status_is_supported(self):
        (self.directory / "0002-reemplazo.md").write_text(VALID.replace("# 1.", "# 2."))
        self.record.write_text(VALID.replace("Accepted", "Superceded by [2. Reemplazo](0002-reemplazo.md)"))
        self.assertEqual(validate(self.directory), [])


class ChangePolicyTests(unittest.TestCase):
    def test_architecture_without_record_fails(self):
        self.assertTrue(change_policy(["compose.yaml"], []))

    def test_architecture_with_updated_record_passes(self):
        self.assertEqual(change_policy(["compose.yaml"], ["docs/adr/0001-ejemplo.md"]), [])

    def test_index_or_template_does_not_replace_a_decision(self):
        for path in ["docs/adr/README.md", "docs/adr/templates/0001-fake.md"]:
            self.assertTrue(change_policy(["compose.yaml"], [path]))

    def test_documentation_only_does_not_require_new_adr(self):
        self.assertEqual(change_policy(["README.md"], []), [])


if __name__ == "__main__":
    unittest.main()
