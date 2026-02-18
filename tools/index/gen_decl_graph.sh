#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

lake env lean --run tools/index/ExtractDeclDeps.lean -- artifacts/graphs/decl_graph.json
