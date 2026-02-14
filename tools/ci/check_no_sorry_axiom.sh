#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[check_no_sorry_axiom] scanning Lean files for forbidden tokens..."
if rg -n --glob '*.lean' '\bsorry\b|\baxiom\b' MLTheory MLTheory.lean; then
  echo "[check_no_sorry_axiom] failed: found forbidden token(s) above."
  exit 1
fi

echo "[check_no_sorry_axiom] passed."
