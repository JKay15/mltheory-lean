#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

python3 tools/index/generate_mathlib_slice.py \
  --repo-root "$ROOT_DIR" \
  --out-dir "$ROOT_DIR/artifacts/index" \
  --top-k 50
