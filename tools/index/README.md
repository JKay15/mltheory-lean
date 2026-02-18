# tools/index

Index and graph generation scripts for vNext exploration workflow.

## MLTheory index (Phase 2/3)

Generate code-first module/import artifacts and the auto docs view:

```bash
tools/index/gen_mltheory_index.sh
```

Generated files:

- `artifacts/index/modules.json`
- `artifacts/index/imports.json`
- `artifacts/index/decls.json` (when `artifacts/graphs/decl_graph.json` exists)
- `artifacts/graphs/module_graph.json`
- `docs/_auto/CodeIndex.md`

## MLTheory -> mathlib structure/slice (Phase 3)

Use the one-shot command:

```bash
tools/index/gen_mathlib_slice.sh
```

Equivalent direct invocation:

```bash
python3 tools/index/generate_mathlib_slice.py --repo-root . --out-dir artifacts/index --top-k 50
```

## Generated files

- `artifacts/index/mathlib_modules.json`
- `artifacts/index/mathlib_imports.json`
- `artifacts/index/mathlib_hubs.json`
- `artifacts/index/mathlib_aggregators.json`
- `artifacts/index/mathlib_slice.json`
- `artifacts/index/mltheory_to_mathlib.json`

## Decl graph (Phase 4)

Generate declaration-level dependency edges:

```bash
tools/index/gen_decl_graph.sh
```

Output:

- `artifacts/graphs/decl_graph.json` (`uses_type` + `uses_value`)

## Subgraph + usage telemetry (PR-5/PR-6 optional)

Generate usage graph, usage-driven suggestions, and merged subgraph:

```bash
tools/index/gen_graph_artifacts.sh
```

Outputs:

- `artifacts/graphs/usage_graph.json`
- `artifacts/index/usage_suggestions.json`
- `artifacts/graphs/subgraph.json`
- `docs/_auto/subgraph.json`
- `docs/_auto/GraphArtifacts.md`
- `docs/GraphExplorer.html` consumes `docs/_auto/subgraph.json` (fallback: `artifacts/graphs/subgraph.json`)

Record one telemetry event (local):

```bash
python3 tools/index/record_usage.py --module MLTheory.Methods.RL.MDP --task card-001 --decl MLTheory.Methods.RL.valueIterationUpdate --status success
```

Local event log path:

- `artifacts/telemetry/usage_events.jsonl`

## Notes

- mathlib path is resolved from `lake-manifest.json` (no hard-coded `.lake/packages/mathlib`).
- imports are parsed from Lean source files (`import A B C` supported).
- slice is computed as closure from direct `Mathlib.*` imports of each `MLTheory*` module.
- generated JSON artifacts should be refreshed by scripts, not hand-edited.
