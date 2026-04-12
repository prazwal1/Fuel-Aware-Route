from __future__ import annotations

import random
from math import hypot

from .graph import FuelGraph


def make_running_example() -> FuelGraph:
    graph = FuelGraph()
    prices = {
        "A": 36.0,
        "B": 44.0,
        "C": 46.0,
        "D": 42.0,
        "E": 24.0,
        "T": 999.0,
    }
    coords = {
        "A": (0.0, 0.0),
        "B": (15.0, 0.0),
        "C": (30.0, 0.0),
        "D": (32.0, -8.0),
        "E": (23.0, -8.0),
        "T": (40.0, 0.0),
    }
    for node, price in prices.items():
        lat, lon = coords[node]
        graph.add_station(node, price, lat=lat, lon=lon)

    graph.add_edge("A", "B", 100)
    graph.add_edge("B", "C", 150)
    graph.add_edge("C", "T", 150)
    graph.add_edge("B", "E", 80)
    graph.add_edge("E", "D", 80)
    graph.add_edge("D", "T", 110)
    return graph


def make_synthetic_graph(
    nodes: int,
    approx_degree: int = 5,
    price_mean: float = 36.0,
    price_sigma_pct: float = 10.0,
    seed: int = 42,
) -> FuelGraph:
    rng = random.Random(seed)
    graph = FuelGraph()
    points: dict[str, tuple[float, float]] = {}
    sigma = price_mean * (price_sigma_pct / 100.0)

    for idx in range(nodes):
        node = f"N{idx}"
        x = rng.random() * 1000.0
        y = rng.random() * 1000.0
        price = max(1.0, rng.gauss(price_mean, sigma))
        points[node] = (x, y)
        graph.add_station(node, price, lat=x, lon=y)

    ids = list(points)
    for idx, node in enumerate(ids):
        distances = []
        x1, y1 = points[node]
        for other in ids:
            if node == other:
                continue
            x2, y2 = points[other]
            distances.append((hypot(x1 - x2, y1 - y2), other))
        distances.sort()
        for distance, other in distances[:approx_degree]:
            graph.add_edge(node, other, distance)

    return graph

