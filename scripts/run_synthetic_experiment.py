from __future__ import annotations

import argparse
from statistics import mean

from ada_route_opt.algorithms import (
    dynamic_programming,
    greedy_refuel,
    partial_fill_astar,
    refuel_astar,
    standard_astar,
    state_expanded_dijkstra,
)
from ada_route_opt.metrics import timed_run
from ada_route_opt.synthetic import make_synthetic_graph


ALGORITHMS = [
    state_expanded_dijkstra,
    greedy_refuel,
    dynamic_programming,
    standard_astar,
    refuel_astar,
    partial_fill_astar,
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=int, default=100)
    parser.add_argument("--degree", type=int, default=5)
    parser.add_argument("--runs", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--price-sigma-pct", type=float, default=10.0)
    parser.add_argument("--tank", type=float, default=40.0)
    parser.add_argument("--initial-fuel", type=float, default=28.0)
    parser.add_argument("--efficiency", type=float, default=10.0)
    args = parser.parse_args()

    graph = make_synthetic_graph(
        nodes=args.nodes,
        approx_degree=args.degree,
        price_sigma_pct=args.price_sigma_pct,
        seed=args.seed,
    )
    source = "N0"
    target = f"N{args.nodes - 1}"

    print(f"source={source} target={target} nodes={args.nodes} runs={args.runs}")
    for algorithm in ALGORITHMS:
        results = [
            timed_run(
                algorithm,
                graph,
                source,
                target,
                args.tank,
                args.initial_fuel,
                args.efficiency,
            )
            for _ in range(args.runs)
        ]
        feasible = [result for result in results if result.feasible]
        avg_cost = mean(result.cost for result in feasible) if feasible else float("inf")
        avg_ms = mean(result.runtime_ms for result in results)
        avg_expanded = mean(result.expanded_states for result in results)
        print(
            f"{results[0].algorithm:20s} feasible={len(feasible):4d}/{args.runs} "
            f"cost={avg_cost:10.2f} runtime_ms={avg_ms:10.3f} expanded={avg_expanded:10.1f}"
        )


if __name__ == "__main__":
    main()

