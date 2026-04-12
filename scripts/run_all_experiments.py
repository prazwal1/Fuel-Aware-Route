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
from ada_route_opt.graph import FuelGraph, RouteResult
from ada_route_opt.metrics import timed_run
from ada_route_opt.synthetic import make_synthetic_graph


Algorithm = Callable[[FuelGraph, str, str, float, float, float], RouteResult]

ALL_ALGORITHMS: list[Algorithm] = [
    state_expanded_dijkstra,
    greedy_refuel,
    dynamic_programming,
    standard_astar,
    refuel_astar,
    partial_fill_astar,
]

RF_VS_PF_ALGORITHMS: list[Algorithm] = [
    refuel_astar,
    partial_fill_astar,
]

VARIABLE_VS_FULL_TANK_ALGORITHMS: list[Algorithm] = [
    state_expanded_dijkstra,
    full_tank_only_dijkstra,
]

FIELDNAMES = [
    "experiment",
    "run",
    "algorithm",
    "feasible",
    "cost",
    "runtime_ms",
    "expanded_states",
    "nodes",
    "degree",
    "sigma_pct",
    "tank_liters",
    "initial_fuel_liters",
    "efficiency_km_per_liter",
    "seed",
    "source",
    "target",
    "path",
]


def compact_row(
    *,
    experiment: str,
    run_idx: int,
    result: RouteResult,
    nodes: int,
    degree: int,
    sigma_pct: float,
    tank_liters: float,
    initial_fuel_liters: float,
    efficiency_km_per_liter: float,
    seed: int,
    source: str,
    target: str,
) -> dict[str, object]:
    return {
        "experiment": experiment,
        "run": run_idx,
        "algorithm": result.algorithm,
        "feasible": result.feasible,
        "cost": result.cost,
        "runtime_ms": result.runtime_ms,
        "expanded_states": result.expanded_states,
        "nodes": nodes,
        "degree": degree,
        "sigma_pct": sigma_pct,
        "tank_liters": tank_liters,
        "initial_fuel_liters": initial_fuel_liters,
        "efficiency_km_per_liter": efficiency_km_per_liter,
        "seed": seed,
        "source": source,
        "target": target,
        "path": "->".join(result.path),
    }


def run_config(
    *,
    writer: csv.DictWriter,
    experiment: str,
    graph: FuelGraph,
    nodes: int,
    degree: int,
    sigma_pct: float,
    tank_liters: float,
    initial_fuel_liters: float,
    efficiency_km_per_liter: float,
    seed: int,
    source: str,
    target: str,
    algorithms: Iterable[Algorithm],
    runs: int,
    warmups: int,
) -> None:
    for algorithm in algorithms:
        for _ in range(warmups):
            timed_run(
                algorithm,
                graph,
                source,
                target,
                tank_liters,
                initial_fuel_liters,
                efficiency_km_per_liter,
            )

        for run_idx in range(runs):
            result = timed_run(
                algorithm,
                graph,
                source,
                target,
                tank_liters,
                initial_fuel_liters,
                efficiency_km_per_liter,
            )
            writer.writerow(
                compact_row(
                    experiment=experiment,
                    run_idx=run_idx,
                    result=result,
                    nodes=nodes,
                    degree=degree,
                    sigma_pct=sigma_pct,
                    tank_liters=tank_liters,
                    initial_fuel_liters=initial_fuel_liters,
                    efficiency_km_per_liter=efficiency_km_per_liter,
                    seed=seed,
                    source=source,
                    target=target,
                )
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--warmups", type=int, default=0)
    parser.add_argument("--output", default="results")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--profile", choices=["smoke", "lite", "proposal"], default="smoke")
    parser.add_argument("--degree", type=int, default=5)
    parser.add_argument("--efficiency", type=float, default=10.0)
    parser.add_argument("--base-nodes", type=int)
    parser.add_argument("--scalability-nodes", default="")
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    result_path = output / "synthetic_results.csv"

    default_scalability_nodes = {
        "smoke": [100, 1000],
        "lite": [100, 300, 1000],
        "proposal": [100, 1000, 10000],
    }
    default_base_nodes = {
        "smoke": 100,
        "lite": 300,
        "proposal": 1000,
    }

    if args.scalability_nodes:
        scalability_nodes = [int(value.strip()) for value in args.scalability_nodes.split(",") if value.strip()]
    else:
        scalability_nodes = default_scalability_nodes[args.profile]
    base_nodes = args.base_nodes if args.base_nodes is not None else default_base_nodes[args.profile]
    source = "N0"
    base_target = f"N{base_nodes - 1}"

    with result_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()

        for nodes in scalability_nodes:
            print(f"experiment=exp1_scalability nodes={nodes}", flush=True)
            graph = make_synthetic_graph(nodes=nodes, approx_degree=args.degree, price_sigma_pct=10.0, seed=args.seed)
            run_config(
                writer=writer,
                experiment="exp1_scalability",
                graph=graph,
                nodes=nodes,
                degree=args.degree,
                sigma_pct=10.0,
                tank_liters=40.0,
                initial_fuel_liters=28.0,
                efficiency_km_per_liter=args.efficiency,
                seed=args.seed,
                source=source,
                target=f"N{nodes - 1}",
                algorithms=ALL_ALGORITHMS,
                runs=args.runs,
                warmups=args.warmups,
            )

        for sigma in [0.0, 5.0, 10.0, 15.0, 20.0]:
            print(f"experiment=exp2_price_variance sigma={sigma}", flush=True)
            graph = make_synthetic_graph(nodes=base_nodes, approx_degree=args.degree, price_sigma_pct=sigma, seed=args.seed)
            run_config(
                writer=writer,
                experiment="exp2_price_variance",
                graph=graph,
                nodes=base_nodes,
                degree=args.degree,
                sigma_pct=sigma,
                tank_liters=40.0,
                initial_fuel_liters=28.0,
                efficiency_km_per_liter=args.efficiency,
                seed=args.seed,
                source=source,
                target=base_target,
                algorithms=ALL_ALGORITHMS,
                runs=args.runs,
                warmups=args.warmups,
            )

        for tank in [20.0, 40.0, 60.0, 80.0]:
            print(f"experiment=exp3_tank_capacity tank={tank}", flush=True)
            graph = make_synthetic_graph(nodes=base_nodes, approx_degree=args.degree, price_sigma_pct=10.0, seed=args.seed)
            run_config(
                writer=writer,
                experiment="exp3_tank_capacity",
                graph=graph,
                nodes=base_nodes,
                degree=args.degree,
                sigma_pct=10.0,
                tank_liters=tank,
                initial_fuel_liters=0.7 * tank,
                efficiency_km_per_liter=args.efficiency,
                seed=args.seed,
                source=source,
                target=base_target,
                algorithms=ALL_ALGORITHMS,
                runs=args.runs,
                warmups=args.warmups,
            )

        for initial_fuel in [10.0, 20.0, 28.0, 40.0]:
            print(f"experiment=exp4_initial_fuel initial={initial_fuel}", flush=True)
            graph = make_synthetic_graph(nodes=base_nodes, approx_degree=args.degree, price_sigma_pct=10.0, seed=args.seed)
            run_config(
                writer=writer,
                experiment="exp4_initial_fuel",
                graph=graph,
                nodes=base_nodes,
                degree=args.degree,
                sigma_pct=10.0,
                tank_liters=40.0,
                initial_fuel_liters=initial_fuel,
                efficiency_km_per_liter=args.efficiency,
                seed=args.seed,
                source=source,
                target=base_target,
                algorithms=ALL_ALGORITHMS,
                runs=args.runs,
                warmups=args.warmups,
            )

        for sigma in [5.0, 10.0, 20.0]:
            for degree in [3, 5, 10, 20]:
                print(f"experiment=exp5_rf_vs_pf sigma={sigma} degree={degree}", flush=True)
                graph = make_synthetic_graph(nodes=base_nodes, approx_degree=degree, price_sigma_pct=sigma, seed=args.seed)
                run_config(
                    writer=writer,
                    experiment="exp5_rf_vs_pf",
                    graph=graph,
                    nodes=base_nodes,
                    degree=degree,
                    sigma_pct=sigma,
                    tank_liters=40.0,
                    initial_fuel_liters=28.0,
                    efficiency_km_per_liter=args.efficiency,
                    seed=args.seed,
                    source=source,
                    target=base_target,
                    algorithms=RF_VS_PF_ALGORITHMS,
                    runs=args.runs,
                    warmups=args.warmups,
                )

        for sigma in [0.0, 5.0, 10.0, 20.0]:
            for tank in [20.0, 40.0, 60.0, 80.0]:
                print(f"experiment=exp7_variable_vs_full_tank sigma={sigma} tank={tank}", flush=True)
                graph = make_synthetic_graph(nodes=base_nodes, approx_degree=args.degree, price_sigma_pct=sigma, seed=args.seed)
                run_config(
                    writer=writer,
                    experiment="exp7_variable_vs_full_tank",
                    graph=graph,
                    nodes=base_nodes,
                    degree=args.degree,
                    sigma_pct=sigma,
                    tank_liters=tank,
                    initial_fuel_liters=0.7 * tank,
                    efficiency_km_per_liter=args.efficiency,
                    seed=args.seed,
                    source=source,
                    target=base_target,
                    algorithms=VARIABLE_VS_FULL_TANK_ALGORITHMS,
                    runs=args.runs,
                    warmups=args.warmups,
                )

    print(f"Wrote results to {result_path}")


if __name__ == "__main__":
    main()
