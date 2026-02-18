#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

tools/index/gen_mltheory_index.sh
tools/index/gen_graph_artifacts.sh

FILES=(
  "artifacts/index/modules.json"
  "artifacts/index/imports.json"
  "artifacts/index/decls.json"
  "artifacts/index/usage_suggestions.json"
  "artifacts/graphs/module_graph.json"
  "artifacts/graphs/decl_graph.json"
  "artifacts/graphs/usage_graph.json"
  "artifacts/graphs/subgraph.json"
  "docs/_auto/CodeIndex.md"
  "docs/_auto/GraphArtifacts.md"
  "docs/_auto/subgraph.json"
)

if ! git diff --quiet -- "${FILES[@]}"; then
  echo "[check_generated_artifacts] generated artifacts are out of date."
  echo "Re-run: tools/index/gen_mltheory_index.sh && tools/index/gen_graph_artifacts.sh"
  git diff -- "${FILES[@]}" | sed -n '1,200p'
  exit 1
fi

echo "[check_generated_artifacts] passed."
