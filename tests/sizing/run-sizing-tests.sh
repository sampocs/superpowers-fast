#!/usr/bin/env bash
# Sizing smoke test: each prompt must announce the expected tier and invoke
# that tier's entry skill.
#
# Usage: tests/sizing/run-sizing-tests.sh [--dry-run]
#
# Runs real headless Claude Code sessions. Run it only after upstream
# superpowers is uninstalled; a second bootstrap skews the sizing.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
OUTPUT_ROOT="/tmp/superpowers-fast-tests/$(date +%s)/sizing"
MAX_TURNS=3

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

# prompt file | expected tier | expected entry skill
CASES=(
  "simple-button.txt|Simple|quick-change"
  "simple-form-field.txt|Simple|quick-change"
  "medium-admin-page.txt|Medium|brainstorming"
  "medium-retry.txt|Medium|brainstorming"
  "large-backtester.txt|Large|brainstorming"
  "large-order-type.txt|Large|brainstorming"
)

failures=0
for case in "${CASES[@]}"; do
  IFS='|' read -r prompt_file tier skill <<<"$case"
  case_dir="$OUTPUT_ROOT/${prompt_file%.txt}"
  log="$case_dir/claude-output.json"

  if [[ "$DRY_RUN" == true ]]; then
    echo "[dry-run] $prompt_file → expect \"Sizing as $tier\" and skill $skill"
    continue
  fi

  # Each case gets a fresh copy of the fixture project so runs can't interfere
  mkdir -p "$case_dir"
  cp -R "$SCRIPT_DIR/fixture" "$case_dir/project"
  (
    cd "$case_dir/project"
    # CM_SESSION_NAME makes the user-level claude-mux naming ritual skip itself
    CM_SESSION_NAME=sizing-test timeout 300 claude -p "$(cat "$PROMPTS_DIR/$prompt_file")" \
      --plugin-dir "$PLUGIN_DIR" \
      --dangerously-skip-permissions \
      --max-turns "$MAX_TURNS" \
      --output-format stream-json --verbose \
      >"$log" 2>&1 || true
  )

  if grep -qE "Sizing as (\*\*)?${tier}\b" "$log"; then
    echo "  [PASS] $prompt_file announced $tier"
  else
    echo "  [FAIL] $prompt_file did not announce $tier (log: $log)"
    failures=$((failures + 1))
  fi

  if grep -qE "\"skill\":\"([^\"]*:)?${skill}\"" "$log"; then
    echo "  [PASS] $prompt_file invoked $skill"
  else
    echo "  [FAIL] $prompt_file did not invoke $skill (log: $log)"
    failures=$((failures + 1))
  fi
done

if [[ "$failures" -gt 0 ]]; then
  echo "STATUS: FAILED ($failures failure(s))"
  exit 1
fi
echo "STATUS: PASSED"
