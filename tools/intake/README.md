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
# Skip index/graph regeneration in lean-commit/promote-cache stage
python3 tools/intake/intake_v2.py lean-commit \
  --domain learning \
  --problem concentration_gap \
  --skip-artifacts

# Create a batch-replan payload for GPTPro Planner (auto-collect blocked cards from Tasks.yaml)
python3 tools/intake/intake_v2.py stuck-batch \
  --domain learning \
  --problem concentration_gap \
  --batch-id batch-002

# If you need a manual blank template instead of auto-collect:
python3 tools/intake/intake_v2.py stuck-batch \
  --domain learning \
  --problem concentration_gap \
  --batch-id batch-002 \
  --stuck-template

# Apply planner reply back into Tasks/Sketch and recompile gates
python3 tools/intake/intake_v2.py apply-replan \
  --domain learning \
  --problem concentration_gap \
  --batch-id batch-002

# Promote proved leaf lemmas from Sketch.lean to Cache.lean
# Marker format in Sketch.lean:
# -- CACHE_PROMOTE_BEGIN: L1
# theorem ...
# -- CACHE_PROMOTE_END: L1
python3 tools/intake/intake_v2.py promote-cache \
  --domain learning \
  --problem concentration_gap

# Initialize and run a Problem Suite
python3 tools/intake/problem_suite.py init --suite-id firstproof_2026
python3 tools/intake/problem_suite.py run \
  --suite suites/firstproof_2026/suite.yaml \
  --phase research-pack
python3 tools/intake/problem_suite.py run \
  --suite suites/firstproof_2026/suite.yaml \
  --phase lean-commit
python3 tools/intake/problem_suite.py run \
  --suite suites/firstproof_2026/suite.yaml \
  --phase proof-scope
python3 tools/intake/problem_suite.py run \
  --suite suites/firstproof_2026/suite.yaml \
  --phase apply-replan \
  --batch-id batch-002
python3 tools/intake/problem_suite.py run \
  --suite suites/firstproof_2026/suite.yaml \
  --phase promote-cache
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
  proof_scope.json
  stuck_batches/
    batch-001.yaml
    batch-001.applied.json
  intake_manifest.json
```

## Lean Commit contract

- `lean-commit` now validates research quality (no `TODO/TBD/???` placeholders in research pack files).
- `Spec.lean`, `Cache.lean`, `Sketch.lean` are compiled via `lake env lean`.
- `Spec.lean` and `Cache.lean` are additionally checked as proved-only files (no `sorry`/`axiom` tokens).
- `lean-commit` runs the full blocking gate (`lake build`, smoke checks, CI contract scripts, SSOT checks).
- `Sketch.lean` is incubator-only; Core/Methods must not import it.
- `docs/meta/taxonomy.yaml` receives `binds` entries for the new `Spec` module.
- `docs/meta/aliases.yaml` receives retrieval aliases for the new problem.
- By default, `tools/index/gen_mltheory_index.sh` and `tools/index/gen_graph_artifacts.sh` are run to refresh subgraph artifacts.
- `Telemetry.jsonl` appends a minimal `lean_commit_ready` event.
- `stuck-batch` auto mode packs blocked/stuck task cards into `stuck_batches/*.yaml` (`items`), so GPTPro can replan multiple blockers in one batch.
- `apply-replan` consumes `planner_reply` (`split_into`/`hints`/`required_defs`), appends split cards into `Tasks.yaml`, upserts planner blocks into `Sketch.lean`, recompiles `Spec/Cache/Sketch`, and emits `stuck_batches/<batch>.applied.json`.
- `promote-cache` consumes explicit markers in `Sketch.lean` (`CACHE_PROMOTE_BEGIN/END`), moves proved blocks into `Cache.lean`, leaves promotion markers in `Sketch.lean`, reruns compile/gates, and refreshes artifacts by default.
- Intake emits `domains_guess`, `domain_confidence`, and `domain_inference_mode` in manifest/tasks for auditable domain classification.
- `proof-scope` materializes `proof_scope.json` with Domain Profile boundaries and widening path:
  `domain_local -> domain_mathlib_slice -> adjacent_domains -> full_mltheory -> full_mathlib -> external_semantic`.
