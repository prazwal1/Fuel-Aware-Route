from __future__ import annotations

from dataclasses import dataclass, field
from math import inf


@dataclass(frozen=True)
class Station:
    node_id: str
    price: float
    lat: float | None = None
    lon: float | None = None


@dataclass(frozen=True)
class Edge:
    to_node: str
    distance_km: float


@dataclass
class FuelGraph:
    stations: dict[str, Station] = field(default_factory=dict)
    adjacency: dict[str, list[Edge]] = field(default_factory=dict)

    def add_station(
        self,
        node_id: str,
        price: float,
        lat: float | None = None,
        lon: float | None = None,
    ) -> None:
        self.stations[node_id] = Station(node_id=node_id, price=price, lat=lat, lon=lon)
        self.adjacency.setdefault(node_id, [])

    def add_edge(self, from_node: str, to_node: str, distance_km: float) -> None:
        if from_node not in self.stations:
            raise KeyError(f"Unknown from_node: {from_node}")
        if to_node not in self.stations:
            raise KeyError(f"Unknown to_node: {to_node}")
        if distance_km < 0:
            raise ValueError("distance_km must be non-negative")
        self.adjacency.setdefault(from_node, []).append(Edge(to_node=to_node, distance_km=distance_km))

    def add_undirected_edge(self, a: str, b: str, distance_km: float) -> None:
        self.add_edge(a, b, distance_km)
        self.add_edge(b, a, distance_km)

    def neighbors(self, node_id: str) -> list[Edge]:
        return self.adjacency.get(node_id, [])

    def price(self, node_id: str) -> float:
        return self.stations[node_id].price

    def min_price(self) -> float:
        if not self.stations:
            return inf
        return min(station.price for station in self.stations.values())


@dataclass
class RouteResult:
    algorithm: str
    cost: float
    path: list[str]
    actions: list[str]
    expanded_states: int
    feasible: bool
    runtime_ms: float = 0.0

    @classmethod
    def infeasible(cls, algorithm: str, expanded_states: int = 0, runtime_ms: float = 0.0) -> "RouteResult":
        return cls(
            algorithm=algorithm,
            cost=inf,
            path=[],
            actions=[],
            expanded_states=expanded_states,
            feasible=False,
            runtime_ms=runtime_ms,
        )

