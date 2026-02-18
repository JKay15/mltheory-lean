#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

if [[ ! -f "${ROOT_DIR}/artifacts/index/modules.json" || ! -f "${ROOT_DIR}/artifacts/graphs/module_graph.json" ]]; then
  tools/index/gen_mltheory_index.sh
fi

if [[ ! -f "${ROOT_DIR}/artifacts/graphs/decl_graph.json" ]]; then
  tools/index/gen_decl_graph.sh || true
fi

if [[ ! -f "${ROOT_DIR}/artifacts/graphs/decl_graph.json" ]]; then
  cat > "${ROOT_DIR}/artifacts/graphs/decl_graph.json" <<'EOF'
{
  "generated_by": "gen_graph_artifacts.sh",
  "nodes": [],
  "edges": [],
  "node_count": 0,
  "edge_count": 0
}
EOF
fi

python3 tools/index/gen_usage_graph.py \
  --events "${ROOT_DIR}/artifacts/telemetry/usage_events.jsonl" \
  --decl-graph "${ROOT_DIR}/artifacts/graphs/decl_graph.json" \
  --out "${ROOT_DIR}/artifacts/graphs/usage_graph.json" \
  --suggestions-out "${ROOT_DIR}/artifacts/index/usage_suggestions.json"

python3 tools/index/gen_subgraph.py \
  --module-graph "${ROOT_DIR}/artifacts/graphs/module_graph.json" \
  --decl-graph "${ROOT_DIR}/artifacts/graphs/decl_graph.json" \
  --usage-graph "${ROOT_DIR}/artifacts/graphs/usage_graph.json" \
  --modules "${ROOT_DIR}/artifacts/index/modules.json" \
  --taxonomy "${ROOT_DIR}/docs/meta/taxonomy.yaml" \
  --canon "${ROOT_DIR}/docs/meta/canon.yaml" \
  --mathlib-slice "${ROOT_DIR}/artifacts/index/mathlib_slice.json" \
  --mathlib-imports "${ROOT_DIR}/artifacts/index/mathlib_imports.json" \
  --mathlib-hubs "${ROOT_DIR}/artifacts/index/mathlib_hubs.json" \
  --mathlib-aggregators "${ROOT_DIR}/artifacts/index/mathlib_aggregators.json" \
  --mltheory-to-mathlib "${ROOT_DIR}/artifacts/index/mltheory_to_mathlib.json" \
  --max-mathlib-modules 220 \
  --out "${ROOT_DIR}/artifacts/graphs/subgraph.json" \
  --export-docs-data "${ROOT_DIR}/docs/_auto/subgraph.json"

python3 tools/index/render_graph_auto_docs.py \
  --subgraph "${ROOT_DIR}/artifacts/graphs/subgraph.json" \
  --usage-graph "${ROOT_DIR}/artifacts/graphs/usage_graph.json" \
  --usage-suggestions "${ROOT_DIR}/artifacts/index/usage_suggestions.json" \
  --out "${ROOT_DIR}/docs/_auto/GraphArtifacts.md"

echo "[gen_graph_artifacts] done"
