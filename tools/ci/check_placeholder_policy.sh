#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

STRICT_DOCSTRING_KEYWORDS="${STRICT_DOCSTRING_KEYWORDS:-0}"

echo "[check_placeholder_policy] checking Lean sources under Core/Methods..."
if rg -n ':\s*Prop\s*:=\s*True\b' MLTheory/Core MLTheory/Methods; then
  echo "[check_placeholder_policy] failed: Core/Methods contains Prop := True placeholders."
  exit 1
fi

if rg -n '\b(theorem|lemma)\s+\w*Placeholder\w*\b' MLTheory/Core MLTheory/Methods; then
  echo "[check_placeholder_policy] failed: Core/Methods contains Placeholder theorem/lemma names."
  exit 1
fi

DOCSTRING_KEYWORD_PATTERN='(?i)^\s*(/--|--)\s*.*\b(hook|placeholder)\b'
DOCSTRING_MATCHES="$(rg -n --pcre2 "${DOCSTRING_KEYWORD_PATTERN}" MLTheory/Core MLTheory/Methods || true)"
if [[ -n "${DOCSTRING_MATCHES}" ]]; then
  if [[ "${STRICT_DOCSTRING_KEYWORDS}" == "1" ]]; then
    echo "${DOCSTRING_MATCHES}"
    echo "[check_placeholder_policy] failed: Core/Methods comments contain hook/placeholder keywords (STRICT_DOCSTRING_KEYWORDS=1)."
    exit 1
  fi
  echo "[check_placeholder_policy] warning: Core/Methods comments still contain hook/placeholder keywords."
  echo "[check_placeholder_policy] warning: set STRICT_DOCSTRING_KEYWORDS=1 to enforce as hard gate."
fi

echo "[check_placeholder_policy] passed."
