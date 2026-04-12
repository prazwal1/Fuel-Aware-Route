from __future__ import annotations

from math import isclose

from ada_route_opt.algorithms import (
    dynamic_programming,
    partial_fill_astar,
    refuel_astar,
    state_expanded_dijkstra,
)
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

