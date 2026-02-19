# Graph UI Artifact Mirror

This directory is a generated mirror for Graph Explorer runtime data.

- `src/index.template.html` + `src/app.js` are the source-of-truth inputs.
- `python3 tools/graph_ui/build_graph_ui.py --write` renders:
  - `docs/GraphExplorer.html`
  - `dist/index.html`
- `dist/_auto/*` and `public/_auto/*` are synced by `tools/index/gen_graph_artifacts.sh`.

Do not edit mirrored files manually.
Regenerate with:

```bash
python3 tools/graph_ui/build_graph_ui.py --write
tools/index/gen_graph_artifacts.sh
```
