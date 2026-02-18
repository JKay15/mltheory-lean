# tools/index

Index and graph generation scripts for vNext exploration workflow.

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


## Notes

- mathlib path is resolved from `lake-manifest.json` (no hard-coded `.lake/packages/mathlib`).
- imports are parsed from Lean source files (`import A B C` supported).
- slice is computed as closure from direct `Mathlib.*` imports of each `MLTheory*` module.
