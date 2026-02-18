#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[check_placeholder_policy] checking Lean sources under Core/Methods..."
if rg -n ':\s*Prop\s*:=\s*True\b' MLTheory/Core MLTheory/Methods; then
  echo "[check_placeholder_policy] failed: Core/Methods contains Prop := True placeholders."
  exit 1
fi

echo "[check_placeholder_policy] passed."
