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
  --domains "${ROOT_DIR}/docs/meta/domains.yaml" \
  --mathlib-slice "${ROOT_DIR}/artifacts/index/mathlib_slice.json" \
  --mathlib-imports "${ROOT_DIR}/artifacts/index/mathlib_imports.json" \
  --mathlib-hubs "${ROOT_DIR}/artifacts/index/mathlib_hubs.json" \
  --mathlib-aggregators "${ROOT_DIR}/artifacts/index/mathlib_aggregators.json" \
  --mltheory-to-mathlib "${ROOT_DIR}/artifacts/index/mltheory_to_mathlib.json" \
  --max-mathlib-modules 220 \
  --out "${ROOT_DIR}/artifacts/graphs/subgraph.json" \
  --export-docs-data "${ROOT_DIR}/docs/_auto/subgraph.json"

python3 tools/index/gen_subgraph_js.py \
  --subgraph "${ROOT_DIR}/docs/_auto/subgraph.json" \
  --out "${ROOT_DIR}/docs/_auto/subgraph.js"

python3 tools/index/render_graph_auto_docs.py \
  --subgraph "${ROOT_DIR}/artifacts/graphs/subgraph.json" \
  --usage-graph "${ROOT_DIR}/artifacts/graphs/usage_graph.json" \
  --usage-suggestions "${ROOT_DIR}/artifacts/index/usage_suggestions.json" \
  --out "${ROOT_DIR}/docs/_auto/GraphArtifacts.md"

GRAPH_UI_PUBLIC_AUTO="${ROOT_DIR}/tools/graph_ui/public/_auto"
GRAPH_UI_DIST_DIR="${ROOT_DIR}/tools/graph_ui/dist"
GRAPH_UI_DIST_AUTO="${GRAPH_UI_DIST_DIR}/_auto"
mkdir -p "${GRAPH_UI_PUBLIC_AUTO}" "${GRAPH_UI_DIST_AUTO}"

cp "${ROOT_DIR}/docs/_auto/subgraph.json" "${GRAPH_UI_PUBLIC_AUTO}/subgraph.json"
cp "${ROOT_DIR}/docs/_auto/subgraph.js" "${GRAPH_UI_PUBLIC_AUTO}/subgraph.js"
cp "${ROOT_DIR}/docs/_auto/subgraph.json" "${GRAPH_UI_DIST_AUTO}/subgraph.json"
cp "${ROOT_DIR}/docs/_auto/subgraph.js" "${GRAPH_UI_DIST_AUTO}/subgraph.js"
cp "${ROOT_DIR}/docs/GraphExplorer.html" "${GRAPH_UI_DIST_DIR}/index.html"

cp "${ROOT_DIR}/artifacts/graphs/decl_graph.json" "${GRAPH_UI_PUBLIC_AUTO}/decl_graph.json"
cp "${ROOT_DIR}/artifacts/graphs/decl_graph.json" "${GRAPH_UI_DIST_AUTO}/decl_graph.json"
cp "${ROOT_DIR}/docs/meta/domains.yaml" "${GRAPH_UI_PUBLIC_AUTO}/domains.yaml"
cp "${ROOT_DIR}/docs/meta/domains.yaml" "${GRAPH_UI_DIST_AUTO}/domains.yaml"

if [[ -f "${ROOT_DIR}/artifacts/index/mathlib_slice.json" ]]; then
  cp "${ROOT_DIR}/artifacts/index/mathlib_slice.json" "${GRAPH_UI_PUBLIC_AUTO}/mathlib_slice.json"
  cp "${ROOT_DIR}/artifacts/index/mathlib_slice.json" "${GRAPH_UI_DIST_AUTO}/mathlib_slice.json"
fi

echo "[gen_graph_artifacts] done"
