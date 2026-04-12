#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PROFILE="${PROFILE:-smoke}"
RUNS="${RUNS:-10}"
WARMUPS="${WARMUPS:-0}"
OUTPUT="${OUTPUT:-results}"
SEED="${SEED:-42}"
DEGREE="${DEGREE:-5}"
BASE_NODES="${BASE_NODES:-}"
SCALABILITY_NODES="${SCALABILITY_NODES:-}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed or not on PATH."
  echo "Install it from https://docs.astral.sh/uv/ and rerun this script."
  exit 1
fi

echo "Project root: $PROJECT_ROOT"
echo "Ensuring Python 3.11 is available through uv..."
uv python install 3.11

echo "Creating/updating .venv..."
uv venv --python 3.11

echo "Installing project dependencies..."
uv pip install -r requirements.txt -e .

echo "Running correctness tests..."
uv run pytest -q

args=(
  scripts/run_all_experiments.py
  --profile "$PROFILE"
  --runs "$RUNS"
  --warmups "$WARMUPS"
  --output "$OUTPUT"
  --seed "$SEED"
  --degree "$DEGREE"
)

if [[ -n "$BASE_NODES" ]]; then
  args+=(--base-nodes "$BASE_NODES")
fi

if [[ -n "$SCALABILITY_NODES" ]]; then
  args+=(--scalability-nodes "$SCALABILITY_NODES")
fi

echo "Running synthetic experiments..."
uv run python "${args[@]}"

echo "Finished. Results are in: $OUTPUT/synthetic_results.csv"

