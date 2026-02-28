#!/bin/bash
# pre-push hook for ATDD Gate (cross-stack, no side-effects)
# Install:
#   cp assets/pre-push-hook-atdd.sh .git/hooks/pre-push
#   chmod +x .git/hooks/pre-push
#
# Principle: gates validate only (boolean output), do NOT modify workspace files.

set -euo pipefail

ATDD_TEST_CMD=${ATDD_TEST_CMD:-"pytest tests/atdd --junitxml=test-results/junit.xml"}
ATDD_JUNIT_PATH=${ATDD_JUNIT_PATH:-"test-results/junit.xml"}

mkdir -p "$(dirname "$ATDD_JUNIT_PATH")"

echo "=== Gate A: Parity Check ==="
if ! python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd --parity-only; then
  echo "Gate A failed: TEST_PLAN.md and tests/atdd are not in parity." >&2
  exit 1
fi

echo "=== Run ATDD Tests ==="
echo "Command: $ATDD_TEST_CMD"
# shellcheck disable=SC2086
if ! bash -lc "$ATDD_TEST_CMD"; then
  echo "ATDD tests failed." >&2
  exit 1
fi

echo "=== Gate B: JUnit Boolean Check (dry-run) ==="
if ! python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd \
  --junit "$ATDD_JUNIT_PATH" --strict --dry-run; then
  echo "Gate B failed: at least one ATDD item is not passing." >&2
  exit 1
fi

echo "All gates passed (no side-effects)."
