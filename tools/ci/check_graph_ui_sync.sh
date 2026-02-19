#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

SRC="docs/GraphExplorer.html"
DIST="tools/graph_ui/dist/index.html"

if [[ ! -f "${SRC}" ]]; then
  echo "[check_graph_ui_sync] missing source file: ${SRC}"
  exit 1
fi

if [[ ! -f "${DIST}" ]]; then
  echo "[check_graph_ui_sync] missing dist mirror file: ${DIST}"
  exit 1
fi

if ! cmp -s "${SRC}" "${DIST}"; then
  echo "[check_graph_ui_sync] failed: ${DIST} is out of sync with ${SRC}."
  echo "Re-run: tools/index/gen_graph_artifacts.sh"
  diff -u "${SRC}" "${DIST}" | sed -n '1,200p'
  exit 1
fi

echo "[check_graph_ui_sync] passed."
