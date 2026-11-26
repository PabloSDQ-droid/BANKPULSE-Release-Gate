#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
if [[ ! -x .tools/adr-tools/src/adr ]]; then
  echo 'Run bash scripts/install-adr-tools.sh first.' >&2
  exit 1
fi
export LC_ALL=C
exec .tools/adr-tools/src/adr "$@"
