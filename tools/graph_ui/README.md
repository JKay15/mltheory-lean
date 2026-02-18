# Graph UI Artifact Mirror

This directory is a generated mirror for Graph Explorer runtime data.

- `dist/index.html` is synced from `docs/GraphExplorer.html`.
- `dist/_auto/*` and `public/_auto/*` are synced by `tools/index/gen_graph_artifacts.sh`.

Do not edit mirrored files manually.
Regenerate with:

```bash
tools/index/gen_graph_artifacts.sh
```
