#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REGISTRY="$ROOT_DIR/docs/ssot/registry.json"
MIGRATOR="$ROOT_DIR/tools/docs/migrate_ssot_to_taxonomy_v2.py"

if [[ ! -f "$REGISTRY" ]]; then
  echo "[check_ssot_migration_idempotent] registry not found: $REGISTRY" >&2
  exit 1
fi
if [[ ! -f "$MIGRATOR" ]]; then
  echo "[check_ssot_migration_idempotent] migrator not found: $MIGRATOR" >&2
  exit 1
fi

TMP_REGISTRY="$(mktemp "${TMPDIR:-/tmp}/registry.migration.XXXXXX.json")"
trap 'rm -f "$TMP_REGISTRY"' EXIT

cp "$REGISTRY" "$TMP_REGISTRY"
python3 "$MIGRATOR" --registry "$TMP_REGISTRY" >/dev/null

if ! diff -u "$REGISTRY" "$TMP_REGISTRY" >/dev/null; then
  echo "[check_ssot_migration_idempotent] failed: migration script rewrites current registry." >&2
  diff -u "$REGISTRY" "$TMP_REGISTRY" | sed -n '1,120p' >&2 || true
  exit 1
fi

echo "[check_ssot_migration_idempotent] passed."
