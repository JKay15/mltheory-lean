# Intake v2 (Research Pack -> Lean Commit)

This helper implements the two-stage Intake pipeline:

1. `research-pack`: create auditable research templates.
2. `lean-commit`: generate compilable Lean artifacts and commit metadata updates.

## Commands

```bash
# Stage A: create Research Pack templates
python3 tools/intake/intake_v2.py research-pack \
  --domain learning \
  --problem concentration_gap \
  --title "Concentration Gap Problem"

# Stage B: generate Lean Commit files after research pack is filled
# (index/graph artifacts refresh is enabled by default)
python3 tools/intake/intake_v2.py lean-commit \
  --domain learning \
  --problem concentration_gap \
  --title "Concentration Gap Problem" \
  --domains learning,probability

# Optional: provide statement text as domain inference signal
python3 tools/intake/intake_v2.py research-pack \
  --domain learning \
  --problem concentration_gap \
  --title "Concentration Gap Problem" \
  --statement-file suites/firstproof_2026/problems/concentration_gap/statement.md
```

Optional:

```bash
# Skip index/graph regeneration in lean-commit stage
python3 tools/intake/intake_v2.py lean-commit \
  --domain learning \
  --problem concentration_gap \
  --skip-artifacts

# Create a new batch-replan payload for GPTPro Planner
python3 tools/intake/intake_v2.py stuck-batch \
  --domain learning \
  --problem concentration_gap \
  --batch-id batch-002

# Initialize and run a Problem Suite
python3 tools/intake/problem_suite.py init --suite-id firstproof_2026
python3 tools/intake/problem_suite.py run \
  --suite suites/firstproof_2026/suite.yaml \
  --phase research-pack
python3 tools/intake/problem_suite.py run \
  --suite suites/firstproof_2026/suite.yaml \
  --phase lean-commit
```

## Generated layout

```text
Incubator/<Domain>/<Problem>/
  statement.md
  Blueprint.md
  research/
    sources.md
    glossary.yaml
    outline.md
    candidate_lemmas.md
    gaps.md
  Spec.lean
  Sketch.lean
  Cache.lean
  Tasks.yaml
  Telemetry.jsonl
  stuck_batches/
    batch-001.yaml
  intake_manifest.json
```

## Lean Commit contract

- `lean-commit` now validates research quality (no `TODO/TBD/???` placeholders in research pack files).
- `Spec.lean`, `Cache.lean`, `Sketch.lean` are compiled via `lake env lean`.
- `lean-commit` runs the full blocking gate (`lake build`, smoke checks, CI contract scripts, SSOT checks).
- `Sketch.lean` is incubator-only; Core/Methods must not import it.
- `docs/meta/taxonomy.yaml` receives `binds` entries for the new `Spec` module.
- `docs/meta/aliases.yaml` receives retrieval aliases for the new problem.
- By default, `tools/index/gen_mltheory_index.sh` and `tools/index/gen_graph_artifacts.sh` are run to refresh subgraph artifacts.
- `Telemetry.jsonl` appends a minimal `lean_commit_ready` event.
- `stuck_batches/*.yaml` is the planner batch input for GPTPro-style replan (Codex consumes planner output and continues high-frequency proving).
- Intake emits `domains_guess`, `domain_confidence`, and `domain_inference_mode` in manifest/tasks for auditable domain classification.
