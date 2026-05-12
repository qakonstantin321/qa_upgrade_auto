#!/usr/bin/env bash
# Quality gate: минимальный процент покрытия API по Swagger (метрики из JSON).
# Использование: check_swagger_coverage_gate.sh <metrics.json> <min_percent>
# Пример: check_swagger_coverage_gate.sh target/swagger-coverage-metrics.json 50
set -euo pipefail

METRICS="${1:?path to swagger-coverage-metrics.json}"
MIN="${2:?minimum coverage_percent}"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required (sudo apt install jq / brew install jq)"
  exit 1
fi

if [[ ! -f "$METRICS" ]]; then
  echo "Metrics file not found: $METRICS"
  exit 1
fi

ERR="$(jq -r '.error // false' "$METRICS")"
if [[ "$ERR" == "true" ]]; then
  echo "Swagger/OpenAPI failed to load (error=true in metrics). Gate failed."
  exit 1
fi

PCT="$(jq -r '.coverage_percent | tonumber' "$METRICS")"

awk -v p="$PCT" -v m="$MIN" 'BEGIN {
  exit((p + 0) < (m + 0) ? 1 : 0)
}' || {
  echo "API coverage ${PCT}% is below minimum ${MIN}% (Swagger endpoints)."
  exit 1
}

echo "API coverage gate OK: ${PCT}% (minimum ${MIN}%)"
