from __future__ import annotations

import heapq
from collections import defaultdict
from math import ceil, hypot, inf
from typing import Callable

from .graph import FuelGraph, RouteResult

State = tuple[str, int]
Parent = dict[State, tuple[State, str]]


def _units(liters: float, step: float, *, mode: str = "round") -> int:
    # Store fuel as discrete integer units so heap states remain hashable and comparable.
    value = liters / step
    if mode == "ceil":
        return int(ceil(value - 1e-12))
    return int(round(value))


def _fuel_needed_units(distance_km: float, efficiency_km_per_liter: float, step: float) -> int:
    return _units(distance_km / efficiency_km_per_liter, step, mode="ceil")


def _reconstruct(parent: Parent, goal: State) -> tuple[list[str], list[str]]:
    # Parent pointers track fuel states; the returned path collapses repeated station IDs.
    states: list[State] = [goal]
    actions: list[str] = []
    current = goal
    while current in parent:
        previous, action = parent[current]
        actions.append(action)
        states.append(previous)
        current = previous
    states.reverse()
    actions.reverse()

    path: list[str] = []
    for node_id, _fuel in states:
        if not path or path[-1] != node_id:
            path.append(node_id)
    return path, actions


def _euclidean_lower_bound_km(graph: FuelGraph, node: str, target: str) -> float:
    a = graph.stations[node]
    b = graph.stations[target]
    if a.lat is None or a.lon is None or b.lat is None or b.lon is None:
        return 0.0
    return hypot(a.lat - b.lat, a.lon - b.lon)


def _reachable_min_price(graph: FuelGraph, node: str, fuel_units: int, efficiency: float, step: float) -> float:
    # PF-A* uses only stations reachable with the current fuel as a local lower-bound price.
    best = graph.price(node)
    for edge in graph.neighbors(node):
        needed = _fuel_needed_units(edge.distance_km, efficiency, step)
        if needed <= fuel_units:
            best = min(best, graph.price(edge.to_node))
    return best


def _run_best_first(
    graph: FuelGraph,
    source: str,
    target: str,
    tank_capacity_liters: float,
    initial_fuel_liters: float,
    efficiency_km_per_liter: float,
    fuel_step_liters: float,
    heuristic: Callable[[str, int], float],
    algorithm_name: str,
) -> RouteResult:
    capacity = _units(tank_capacity_liters, fuel_step_liters)
    initial = min(_units(initial_fuel_liters, fuel_step_liters), capacity)
    start: State = (source, initial)

    best_cost: dict[State, float] = defaultdict(lambda: inf)
    parent: Parent = {}
    best_cost[start] = 0.0
    heap: list[tuple[float, float, str, int]] = [(heuristic(source, initial), 0.0, source, initial)]
    expanded = 0

    while heap:
        _priority, cost, node, fuel = heapq.heappop(heap)
        state = (node, fuel)
        # Skip stale heap entries left behind after a better path to the same state was found.
        if cost != best_cost[state]:
            continue
        expanded += 1
        if node == target:
            path, actions = _reconstruct(parent, state)
            return RouteResult(algorithm_name, cost, path, actions, expanded, True)

        for edge in graph.neighbors(node):
            needed = _fuel_needed_units(edge.distance_km, efficiency_km_per_liter, fuel_step_liters)
            if needed <= fuel:
                # Driving transitions preserve monetary cost and reduce only the fuel dimension.
                next_state = (edge.to_node, fuel - needed)
                if cost < best_cost[next_state]:
                    best_cost[next_state] = cost
                    parent[next_state] = (state, f"drive {node}->{edge.to_node}, use {needed * fuel_step_liters:.2f} L")
                    priority = cost + heuristic(next_state[0], next_state[1])
                    heapq.heappush(heap, (priority, cost, next_state[0], next_state[1]))

        for buy_units in range(1, capacity - fuel + 1):
            # Purchase transitions stay at the same node and enumerate each feasible fill amount.
            next_fuel = fuel + buy_units
            buy_cost = buy_units * fuel_step_liters * graph.price(node)
            next_cost = cost + buy_cost
            next_state = (node, next_fuel)
            if next_cost < best_cost[next_state]:
                best_cost[next_state] = next_cost
                parent[next_state] = (
                    state,
                    f"buy {buy_units * fuel_step_liters:.2f} L at {node} @ {graph.price(node):.2f}",
                )
                priority = next_cost + heuristic(node, next_fuel)
                heapq.heappush(heap, (priority, next_cost, node, next_fuel))

    return RouteResult.infeasible(algorithm_name, expanded)


def state_expanded_dijkstra(
    graph: FuelGraph,
    source: str,
    target: str,
    tank_capacity_liters: float,
    initial_fuel_liters: float,
    efficiency_km_per_liter: float = 10.0,
    fuel_step_liters: float = 1.0,
) -> RouteResult:
    return _run_best_first(
        graph,
        source,
        target,
        tank_capacity_liters,
        initial_fuel_liters,
        efficiency_km_per_liter,
        fuel_step_liters,
        heuristic=lambda _node, _fuel: 0.0,
        algorithm_name="dijkstra",
    )


def full_tank_only_dijkstra(
    graph: FuelGraph,
    source: str,
    target: str,
    tank_capacity_liters: float,
    initial_fuel_liters: float,
    efficiency_km_per_liter: float = 10.0,
    fuel_step_liters: float = 1.0,
) -> RouteResult:
    capacity = _units(tank_capacity_liters, fuel_step_liters)
    initial = min(_units(initial_fuel_liters, fuel_step_liters), capacity)
    start: State = (source, initial)

    best_cost: dict[State, float] = defaultdict(lambda: inf)
    parent: Parent = {}
    best_cost[start] = 0.0
    heap: list[tuple[float, str, int]] = [(0.0, source, initial)]
    expanded = 0

    while heap:
        cost, node, fuel = heapq.heappop(heap)
        state = (node, fuel)
        if cost != best_cost[state]:
            continue
        expanded += 1
        if node == target:
            path, actions = _reconstruct(parent, state)
            return RouteResult("full_tank_only_dijkstra", cost, path, actions, expanded, True)

        for edge in graph.neighbors(node):
            needed = _fuel_needed_units(edge.distance_km, efficiency_km_per_liter, fuel_step_liters)
            if needed > capacity:
                continue

            candidates: list[tuple[int, float, str]] = []
            if needed <= fuel:
                candidates.append(
                    (
                        fuel - needed,
                        0.0,
                        f"drive {node}->{edge.to_node}, use {needed * fuel_step_liters:.2f} L",
                    )
                )
            if fuel < capacity:
                buy_units = capacity - fuel
                fill_cost = buy_units * fuel_step_liters * graph.price(node)
                candidates.append(
                    (
                        capacity - needed,
                        fill_cost,
                        f"fill tank at {node}: buy {buy_units * fuel_step_liters:.2f} L @ {graph.price(node):.2f}; "
                        f"drive {node}->{edge.to_node}",
                    )
                )

            for next_fuel, extra_cost, action in candidates:
                next_cost = cost + extra_cost
                next_state = (edge.to_node, next_fuel)
                if next_cost < best_cost[next_state]:
                    best_cost[next_state] = next_cost
                    parent[next_state] = (state, action)
                    heapq.heappush(heap, (next_cost, edge.to_node, next_fuel))

    return RouteResult.infeasible("full_tank_only_dijkstra", expanded)


def astar(
    graph: FuelGraph,
    source: str,
    target: str,
    tank_capacity_liters: float,
    initial_fuel_liters: float,
    efficiency_km_per_liter: float = 10.0,
    fuel_step_liters: float = 1.0,
    algorithm_name: str = "astar",
) -> RouteResult:
    p_min = graph.min_price()

    def heuristic(node: str, _fuel: int) -> float:
        km = _euclidean_lower_bound_km(graph, node, target)
        return (km / efficiency_km_per_liter) * p_min

    return _run_best_first(
        graph,
        source,
        target,
        tank_capacity_liters,
        initial_fuel_liters,
        efficiency_km_per_liter,
        fuel_step_liters,
        heuristic=heuristic,
        algorithm_name=algorithm_name,
    )


def standard_astar(*args, **kwargs) -> RouteResult:
    return astar(*args, **kwargs, algorithm_name="standard_astar")


def refuel_astar(*args, **kwargs) -> RouteResult:
    return astar(*args, **kwargs, algorithm_name="rf_astar")


def partial_fill_astar(
    graph: FuelGraph,
    source: str,
    target: str,
    tank_capacity_liters: float,
    initial_fuel_liters: float,
    efficiency_km_per_liter: float = 10.0,
    fuel_step_liters: float = 1.0,
) -> RouteResult:
    def heuristic(node: str, fuel: int) -> float:
        km = _euclidean_lower_bound_km(graph, node, target)
        required_liters = km / efficiency_km_per_liter
        current_liters = fuel * fuel_step_liters
        deficit = max(required_liters - current_liters, 0.0)
        reachable_price = _reachable_min_price(graph, node, fuel, efficiency_km_per_liter, fuel_step_liters)
        return deficit * reachable_price

    return _run_best_first(
        graph,
        source,
        target,
        tank_capacity_liters,
        initial_fuel_liters,
        efficiency_km_per_liter,
        fuel_step_liters,
        heuristic=heuristic,
        algorithm_name="pf_astar",
    )


def dynamic_programming(
    graph: FuelGraph,
    source: str,
    target: str,
    tank_capacity_liters: float,
    initial_fuel_liters: float,
    efficiency_km_per_liter: float = 10.0,
    fuel_step_liters: float = 1.0,
) -> RouteResult:
    # The state-expanded shortest-path formulation is the DP recurrence evaluated with a heap.
    result = state_expanded_dijkstra(
        graph,
        source,
        target,
        tank_capacity_liters,
        initial_fuel_liters,
        efficiency_km_per_liter,
        fuel_step_liters,
    )
    result.algorithm = "dynamic_programming"
    return result


def greedy_refuel(
    graph: FuelGraph,
    source: str,
    target: str,
    tank_capacity_liters: float,
    initial_fuel_liters: float,
    efficiency_km_per_liter: float = 10.0,
    fuel_step_liters: float = 1.0,
) -> RouteResult:
    capacity = _units(tank_capacity_liters, fuel_step_liters)
    fuel = min(_units(initial_fuel_liters, fuel_step_liters), capacity)
    node = source
    cost = 0.0
    path = [source]
    actions: list[str] = []
    expanded = 0
    visited_guard = 0

    while node != target and visited_guard < max(1, len(graph.stations) * capacity * 4):
        visited_guard += 1
        expanded += 1
        reachable_edges = []
        for edge in graph.neighbors(node):
            needed = _fuel_needed_units(edge.distance_km, efficiency_km_per_liter, fuel_step_liters)
            if needed <= capacity:
                reachable_edges.append((edge, needed))
        if not reachable_edges:
            return RouteResult.infeasible("greedy", expanded)

        cheaper = [
            (edge, needed)
            for edge, needed in reachable_edges
            if needed <= fuel and graph.price(edge.to_node) < graph.price(node)
        ]
        if cheaper:
            edge, needed = min(cheaper, key=lambda item: item[1])
        else:
            if fuel < capacity:
                buy = capacity - fuel
                cost += buy * fuel_step_liters * graph.price(node)
                actions.append(f"buy {buy * fuel_step_liters:.2f} L at {node} @ {graph.price(node):.2f}")
                fuel = capacity
            feasible_now = [(edge, needed) for edge, needed in reachable_edges if needed <= fuel]
            if not feasible_now:
                return RouteResult.infeasible("greedy", expanded)
            edge, needed = min(feasible_now, key=lambda item: (graph.price(item[0].to_node), item[1]))

        fuel -= needed
        actions.append(f"drive {node}->{edge.to_node}, use {needed * fuel_step_liters:.2f} L")
        node = edge.to_node
        path.append(node)

    if node != target:
        return RouteResult.infeasible("greedy", expanded)
    return RouteResult("greedy", cost, path, actions, expanded, True)
