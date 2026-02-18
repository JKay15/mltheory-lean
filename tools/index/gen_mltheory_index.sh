#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

python3 tools/index/gen_modules.py \
  --root "${ROOT_DIR}" \
  --src "${ROOT_DIR}/MLTheory" \
  --out "${ROOT_DIR}/artifacts/index/modules.json" \
  --package MLTheory

python3 tools/index/gen_imports.py \
  --src "${ROOT_DIR}/MLTheory" \
  --out "${ROOT_DIR}/artifacts/index/imports.json" \
  --package MLTheory

python3 tools/index/gen_module_graph.py \
  --modules "${ROOT_DIR}/artifacts/index/modules.json" \
  --imports "${ROOT_DIR}/artifacts/index/imports.json" \
  --out "${ROOT_DIR}/artifacts/graphs/module_graph.json"

python3 tools/index/render_auto_docs.py \
  --modules "${ROOT_DIR}/artifacts/index/modules.json" \
  --imports "${ROOT_DIR}/artifacts/index/imports.json" \
  --out "${ROOT_DIR}/docs/_auto/CodeIndex.md"

echo "[gen_mltheory_index] done"
