#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
revision="$(tr -d '\r\n' < "$project_root/scripts/adr-tools-version")"
tools_dir="$project_root/.tools/adr-tools"
[[ "$revision" =~ ^[0-9a-f]{40}$ ]] || { echo 'Invalid ADR Tools revision' >&2; exit 1; }
if [[ ! -d "$tools_dir/.git" ]]; then
  mkdir -p "$project_root/.tools"
  git clone https://github.com/npryce/adr-tools.git "$tools_dir"
fi
[[ "$(git -C "$tools_dir" remote get-url origin)" == 'https://github.com/npryce/adr-tools.git' ]] || {
  echo 'Unexpected ADR Tools origin' >&2; exit 1;
}
if ! git -C "$tools_dir" cat-file -e "$revision^{commit}" 2>/dev/null; then
  git -C "$tools_dir" fetch origin "$revision"
fi
git -C "$tools_dir" checkout --detach "$revision"
[[ "$(git -C "$tools_dir" rev-parse HEAD)" == "$revision" ]]
echo "ADR Tools installed at revision $revision"
