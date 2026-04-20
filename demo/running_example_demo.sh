#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHONPATH=src python3 - <<'PY'
from ada_route_opt.algorithms import (
    dynamic_programming,
    greedy_refuel,
    partial_fill_astar,
    refuel_astar,
    standard_astar,
    state_expanded_dijkstra,
)
from ada_route_opt.synthetic import make_running_example

graph = make_running_example()
algorithms = [
    state_expanded_dijkstra,
    greedy_refuel,
    dynamic_programming,
    standard_astar,
    refuel_astar,
    partial_fill_astar,
]

for algorithm in algorithms:
    result = algorithm(graph, "A", "T", 40.0, 28.0, 10.0)
    print(
        "{:<24} feasible={} cost={} states={} path={}".format(
            result.algorithm,
            result.feasible,
            result.cost,
            result.expanded_states,
            "->".join(result.path),
        )
    )
PY
