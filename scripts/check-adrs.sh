#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
args=()
if [[ -n "${1:-}" ]]; then args+=(--base "$1"); fi
python3 scripts/check_adrs.py "${args[@]}"
index_file="$(mktemp)"
trap 'rm -f "$index_file"' EXIT
bash scripts/adr.sh generate toc > "$index_file"
if ! diff -u docs/adr/README.md "$index_file"; then
  echo 'Regenerate the index: bash scripts/adr.sh generate toc > docs/adr/README.md' >&2
  exit 1
fi
echo 'ADR index OK'
