#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="$PROJECT_ROOT/configs/synthetic_100.env"

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Missing config: $CONFIG_PATH"
  exit 1
fi

set -a
source "$CONFIG_PATH"
set +a

"$PROJECT_ROOT/scripts/run_bash_synthetic_experiments.sh"

