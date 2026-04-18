from __future__ import annotations

import argparse
import csv
from collections.abc import Callable, Iterable
from pathlib import Path

from ada_route_opt.algorithms import (
    dynamic_programming,
    full_tank_only_dijkstra,
    greedy_refuel,
    partial_fill_astar,
    refuel_astar,
    standard_astar,
    state_expanded_dijkstra,
)
from ada_route_opt.graph import RouteResult
from ada_route_opt.metrics import timed_run
from ada_route_opt.real_instances import RealRouteInstance, load_real_instances


Algorithm = Callable[..., RouteResult]

VARIABLE_PURCHASE_ALGORITHMS: list[Algorithm] = [
    state_expanded_dijkstra,
    greedy_refuel,
    dynamic_programming,
    standard_astar,
    refuel_astar,
    partial_fill_astar,
]

FULL_TANK_ALGORITHMS: list[Algorithm] = [
    full_tank_only_dijkstra,
]

FIELDNAMES = [
    "experiment",
    "route_name",
    "instance_id",
    "purchase_model",
    "run",
    "algorithm",
    "feasible",
    "cost",
    "runtime_ms",
    "expanded_states",
    "tank_liters",
    "initial_fuel_liters",
    "efficiency_km_per_liter",
    "source",
    "target",
    "path",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Experiment 6 on real-route instances.")
    parser.add_argument(
        "--instances-dir",
        default="data/real_routes",
        help="Directory containing one JSON file per real-route instance.",
    )
    parser.add_argument("--output", default="results_real")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--warmups", type=int, default=0)
    parser.add_argument(
        "--purchase-model",
        choices=["variable", "full_tank_only", "both"],
        default="both",
    )
    return parser.parse_args()


def selected_algorithms(purchase_model: str) -> list[tuple[str, Iterable[Algorithm]]]:
    if purchase_model == "variable":
        return [("variable", VARIABLE_PURCHASE_ALGORITHMS)]
    if purchase_model == "full_tank_only":
        return [("full_tank_only", FULL_TANK_ALGORITHMS)]
    return [
        ("variable", VARIABLE_PURCHASE_ALGORITHMS),
        ("full_tank_only", FULL_TANK_ALGORITHMS),
    ]


def row_from_result(
    *,
    instance: RealRouteInstance,
    purchase_model: str,
    run_idx: int,
    result: RouteResult,
) -> dict[str, object]:
    return {
        "experiment": "exp6_real_routes",
        "route_name": instance.route_name,
        "instance_id": instance.instance_id,
        "purchase_model": purchase_model,
        "run": run_idx,
        "algorithm": result.algorithm,
        "feasible": result.feasible,
        "cost": result.cost,
        "runtime_ms": result.runtime_ms,
        "expanded_states": result.expanded_states,
        "tank_liters": instance.tank_liters,
        "initial_fuel_liters": instance.initial_fuel_liters,
        "efficiency_km_per_liter": instance.efficiency_km_per_liter,
        "source": instance.source,
        "target": instance.target,
        "path": "->".join(result.path),
    }


def run_instance(
    *,
    writer: csv.DictWriter,
    instance: RealRouteInstance,
    purchase_model: str,
    algorithms: Iterable[Algorithm],
    runs: int,
    warmups: int,
) -> None:
    for algorithm in algorithms:
        for _ in range(warmups):
            timed_run(
                algorithm,
                instance.graph,
                instance.source,
                instance.target,
                instance.tank_liters,
                instance.initial_fuel_liters,
                instance.efficiency_km_per_liter,
            )

        for run_idx in range(runs):
            result = timed_run(
                algorithm,
                instance.graph,
                instance.source,
                instance.target,
                instance.tank_liters,
                instance.initial_fuel_liters,
                instance.efficiency_km_per_liter,
            )
            writer.writerow(
                row_from_result(
                    instance=instance,
                    purchase_model=purchase_model,
                    run_idx=run_idx,
                    result=result,
                )
            )


def main() -> None:
    args = parse_args()
    instances = load_real_instances(args.instances_dir)
    if not instances:
        raise SystemExit(f"No real-route instance JSON files found in {args.instances_dir}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "real_route_results.csv"

    with result_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()

        for instance in instances:
            print(f"experiment=exp6_real_routes route={instance.instance_id}", flush=True)
            for purchase_model, algorithms in selected_algorithms(args.purchase_model):
                run_instance(
                    writer=writer,
                    instance=instance,
                    purchase_model=purchase_model,
                    algorithms=algorithms,
                    runs=args.runs,
                    warmups=args.warmups,
                )

    print(f"Wrote results to {result_path}")


if __name__ == "__main__":
    main()
