#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

python3 tools/graph_ui/build_graph_ui.py --check
echo "[check_graph_ui_source_sync] passed."
