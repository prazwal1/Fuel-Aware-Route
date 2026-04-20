#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHONPATH=src python3 - <<'PY'
from ada_route_opt.algorithms import (
    full_tank_only_dijkstra,
    partial_fill_astar,
    state_expanded_dijkstra,
)
from ada_route_opt.real_instances import load_real_instances

instances = load_real_instances("data/real_routes/generated")

for instance in instances:
    variable = state_expanded_dijkstra(
        instance.graph,
        instance.source,
        instance.target,
        instance.tank_liters,
        instance.initial_fuel_liters,
        instance.efficiency_km_per_liter,
    )
    pf_astar = partial_fill_astar(
        instance.graph,
        instance.source,
        instance.target,
        instance.tank_liters,
        instance.initial_fuel_liters,
        instance.efficiency_km_per_liter,
    )
    full_tank = full_tank_only_dijkstra(
        instance.graph,
        instance.source,
        instance.target,
        instance.tank_liters,
        instance.initial_fuel_liters,
        instance.efficiency_km_per_liter,
    )
    savings_pct = (full_tank.cost - variable.cost) / full_tank.cost * 100
    print(
        "{} | variable={} PF={} full={} saving%={}".format(
            instance.route_name,
            round(variable.cost, 2),
            round(pf_astar.cost, 2),
            round(full_tank.cost, 2),
            round(savings_pct, 2),
        )
    )
PY
