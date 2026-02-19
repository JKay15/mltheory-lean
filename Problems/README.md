# Problems Workspace

Problem folders follow:

```
Problems/<Suite>/<ProblemName>/
  Spec.lean
  Sketch.lean (optional)
  Cache.lean
  Proof.lean
  Tasks.yaml
  Sources.md
  Glossary.yaml
  ProofMap.json (generated)
```

Generate/update proof maps:

```bash
python3 tools/index/gen_proof_map.py
```
