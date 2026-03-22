#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECTIONS=(
  "langgraph-chat"
  "langgraph-debate"
  "langgraph-qna"
  "langgraph-research"
)

for section in "${SECTIONS[@]}"; do
  echo ""
  echo "============================================================"
  echo "Running tests for ${section}"
  echo "============================================================"
  (cd "${ROOT_DIR}/${section}" && pytest -q)
done

echo ""
echo "All section test suites passed."
