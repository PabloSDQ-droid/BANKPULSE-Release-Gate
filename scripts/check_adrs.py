#!/usr/bin/env python3
"""Validation policy for BankPulse, separate from upstream ADR Tools."""
import argparse
from datetime import date
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
FILENAME = re.compile(r"^(\d{4,})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
REQUIRED = ("Status", "Context", "Decision", "Consequences")
PLACEHOLDERS = (
    "The issue motivating this decision", "The change that we're proposing",
    "What becomes easier or more difficult", "Completar contexto",
    "Completar decision", "Completar consecuencias",
)


def validate(directory):
    errors, ids = [], set()
    records = sorted(p for p in directory.glob("*.md") if p.name != "README.md")
    if not records:
        return ["At least one numbered ADR is required"]
    for path in records:
        match = FILENAME.fullmatch(path.name)
        if not match:
            errors.append(f"{path.name}: invalid filename")
            continue
        number = int(match[1])
        if number == 0 or number in ids:
            errors.append(f"{path.name}: duplicate or zero number")
        ids.add(number)
        text = path.read_text(encoding="utf-8")
        if not re.match(rf"\A# {number}\. \S[^\n]*\n", text):
            errors.append(f"{path.name}: title must match the ADR number")
        dates = re.findall(r"^Date: (\d{4}-\d{2}-\d{2})$", text, re.M)
        try:
            if len(dates) != 1:
                raise ValueError()
            date.fromisoformat(dates[0])
        except ValueError:
            errors.append(f"{path.name}: one valid ISO Date is required")
        sections = {}
        headers = list(re.finditer(r"^## ([^\n]+)$", text, re.M))
        for i, header in enumerate(headers):
            name = header[1]
            end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
            if name in sections:
                errors.append(f"{path.name}: duplicate section {name}")
            sections[name] = text[header.end():end].strip()
        for name in REQUIRED:
            if not sections.get(name):
                errors.append(f"{path.name}: missing or empty {name}")
        status = sections.get("Status", "")
        # The upstream tool spells its replacement status 'Superceded by'.
        if not re.match(r"^(Proposed|Accepted|Deprecated|Rejected|Superseded|Superceded by)\b", status):
            errors.append(f"{path.name}: invalid Status")
        if re.match(r"^(Superseded|Superceded by)\b", status) and not re.search(r"\]\([^)]*\.md\)", status):
            errors.append(f"{path.name}: replacement ADR link required")
        if any(p in text for p in PLACEHOLDERS) or re.search(r"\b(TODO|TBD)\b", text):
            errors.append(f"{path.name}: unfilled template")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            if not (path.parent / unquote(parsed.path)).exists():
                errors.append(f"{path.name}: broken local link {target}")
    return errors


def architecture_path(path):
    return (
        path == "compose.yaml"
        or path.startswith((".github/workflows/", ".devcontainer/"))
        or path in {"frontend/Dockerfile", "frontend/nginx.conf", "scripts/smoke.sh",
                    "scripts/business-test.sh", "scripts/technical-smoke.sh",
                    "scripts/check_adrs.py", "scripts/check-adrs.sh",
                    "scripts/install-adr-tools.sh", "scripts/adr.sh", "scripts/adr-tools-version", ".adr-dir"}
        or (path.startswith("services/") and (
            "/src/main/" in path or path.endswith(("/pom.xml", "/Dockerfile"))
        ))
    )


def change_policy(changed_paths, updated_paths):
    architecture = [p for p in changed_paths if architecture_path(p)]
    has_record = any(
        Path(p).parent == Path("docs/adr") and FILENAME.fullmatch(Path(p).name)
        for p in updated_paths
    )
    if architecture and not has_record:
        return ["Architecture-sensitive changes require an added or updated ADR: " + ", ".join(architecture)]
    return []


def git_paths(base, *options):
    output = subprocess.check_output(
        ["git", "diff", "--name-only", "--no-renames", "-z", *options, f"{base}...HEAD", "--"], cwd=ROOT
    )
    return [p.decode("utf-8") for p in output.split(b"\0") if p]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="PR base SHA; check the entire PR diff against HEAD")
    args = parser.parse_args()
    errors = []
    config = ROOT / ".adr-dir"
    if not config.is_file() or config.read_text().strip() != "docs/adr":
        errors.append(".adr-dir must contain docs/adr")
    errors.extend(validate(ROOT / "docs/adr"))
    if args.base:
        errors.extend(change_policy(git_paths(args.base), git_paths(args.base, "--diff-filter=AM")))
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if not errors:
        print("ADR validation OK")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
