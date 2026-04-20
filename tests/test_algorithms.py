from __future__ import annotations

from math import isclose
from pathlib import Path

from ada_route_opt.algorithms import (
    dynamic_programming,
    full_tank_only_dijkstra,
    partial_fill_astar,
    refuel_astar,
    state_expanded_dijkstra,
)
from ada_route_opt.real_instances import load_real_instance
from ada_route_opt.synthetic import make_running_example


def test_running_example_optimal_cost() -> None:
    graph = make_running_example()
    result = state_expanded_dijkstra(graph, "A", "T", 40.0, 28.0, 10.0)
    assert result.feasible
    assert isclose(result.cost, 216.0)
    assert result.path == ["A", "B", "E", "D", "T"]


def test_dp_matches_dijkstra() -> None:
    graph = make_running_example()
    dijkstra = state_expanded_dijkstra(graph, "A", "T", 40.0, 28.0, 10.0)
    dp = dynamic_programming(graph, "A", "T", 40.0, 28.0, 10.0)
    assert dp.feasible
    assert isclose(dp.cost, dijkstra.cost)


def test_rf_and_pf_match_dijkstra_on_running_example() -> None:
    graph = make_running_example()
    dijkstra = state_expanded_dijkstra(graph, "A", "T", 40.0, 28.0, 10.0)
    rf = refuel_astar(graph, "A", "T", 40.0, 28.0, 10.0)
    pf = partial_fill_astar(graph, "A", "T", 40.0, 28.0, 10.0)
    assert rf.feasible
    assert pf.feasible
    assert isclose(rf.cost, dijkstra.cost)
    assert isclose(pf.cost, dijkstra.cost)


def test_real_instance_loader_and_algorithms() -> None:
    instance = load_real_instance(Path("data/real_routes/generated/bkk_to_kkc.json"))
    dijkstra = state_expanded_dijkstra(
        instance.graph,
        instance.source,
        instance.target,
        instance.tank_liters,
        instance.initial_fuel_liters,
        instance.efficiency_km_per_liter,
    )
    pf = partial_fill_astar(
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
    assert instance.instance_id == "bkk_to_kkc"
    assert instance.route_name == "Bangkok to Khon Kaen"
    assert dijkstra.feasible
    assert pf.feasible
    assert full_tank.feasible
    assert isclose(pf.cost, dijkstra.cost)
