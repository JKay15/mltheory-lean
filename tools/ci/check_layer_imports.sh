#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

status=0

echo "[check_layer_imports] checking Core boundary imports..."
if rg -n '^import\s+MLTheory(\s|$)' MLTheory/Core; then
  echo "[check_layer_imports] failed: Core layer must not import top-level MLTheory."
  status=1
fi
if rg -n '^import\s+MLTheory\.(Methods|Applications|Books|Probability|Statistics|OR|Learning|AI|LLM|OCO|RL|Bandits|HDP|Concentration|Optimization|InfoTheory)\b' MLTheory/Core; then
  echo "[check_layer_imports] failed: Core layer imports non-core modules."
  status=1
fi

echo "[check_layer_imports] checking Methods boundary imports..."
if rg -n '^import\s+MLTheory(\s|$)' MLTheory/Methods; then
  echo "[check_layer_imports] failed: Methods layer must not import top-level MLTheory."
  status=1
fi
if rg -n '^import\s+MLTheory\.(Applications|Books|Probability|Statistics|OR|Learning|AI|LLM|OCO|RL|Bandits|HDP|Concentration|Optimization|InfoTheory)\b' MLTheory/Methods; then
  echo "[check_layer_imports] failed: Methods layer imports non-core/non-method modules."
  status=1
fi

echo "[check_layer_imports] checking cross-repo leakage..."
if rg -n '^import\s+Paper\.' MLTheory MLTheory.lean; then
  echo "[check_layer_imports] failed: MLTheory must not import paper-template namespaces."
  status=1
fi

if [[ "$status" -ne 0 ]]; then
  exit 1
fi

echo "[check_layer_imports] passed."
