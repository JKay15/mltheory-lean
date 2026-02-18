#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f "${ROOT_DIR}/artifacts/index/modules.json" ]]; then
  tools/index/gen_mltheory_index.sh
fi

IMPORT_MODULES=()
while IFS= read -r module; do
  if [[ -n "${module}" ]]; then
    IMPORT_MODULES+=("${module}")
  fi
done < <(python3 - <<'PY'
import json
from pathlib import Path

path = Path("artifacts/index/modules.json")
data = json.loads(path.read_text(encoding="utf-8"))
mods = []
seen = set()
for row in data.get("modules", []):
    if not isinstance(row, dict):
        continue
    module = row.get("module")
    if not isinstance(module, str):
        continue
    if not (module.startswith("MLTheory.") or module.startswith("Incubator.")):
        continue
    if module in seen:
        continue
    seen.add(module)
    mods.append(module)
for module in sorted(mods):
    print(module)
PY
)

if [[ -d "${ROOT_DIR}/Incubator" ]] && find "${ROOT_DIR}/Incubator" -type f -name '*.lean' | grep -q .; then
  while IFS= read -r lean_file; do
    [[ -z "${lean_file}" ]] && continue
    rel="${lean_file#${ROOT_DIR}/}"
    out_olean="${ROOT_DIR}/.lake/build/lib/lean/${rel%.lean}.olean"
    mkdir -p "$(dirname "${out_olean}")"
    lake env lean -o "${out_olean}" "${rel}" >/dev/null
  done < <(find "${ROOT_DIR}/Incubator" -type f -name '*.lean' | sort)
fi

lake env lean --run tools/index/ExtractDeclDeps.lean -- artifacts/graphs/decl_graph.json "${IMPORT_MODULES[@]}"
