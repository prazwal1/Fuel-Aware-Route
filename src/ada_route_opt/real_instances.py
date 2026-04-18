from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .graph import FuelGraph


@dataclass(frozen=True)
class RealRouteInstance:
    instance_id: str
    route_name: str
    source: str
    target: str
    tank_liters: float
    initial_fuel_liters: float
    efficiency_km_per_liter: float
    graph: FuelGraph


def load_real_instance(path: str | Path) -> RealRouteInstance:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    graph = FuelGraph()
    for station in payload["stations"]:
        graph.add_station(
            station["node_id"],
            float(station["price"]),
            lat=station.get("lat"),
            lon=station.get("lon"),
        )

    for edge in payload["edges"]:
        graph.add_edge(
            edge["from_node"],
            edge["to_node"],
            float(edge["distance_km"]),
        )

    defaults = payload.get("vehicle", {})
    return RealRouteInstance(
        instance_id=payload["instance_id"],
        route_name=payload.get("route_name", payload["instance_id"]),
        source=payload["source"],
        target=payload["target"],
        tank_liters=float(defaults.get("tank_liters", 40.0)),
        initial_fuel_liters=float(defaults.get("initial_fuel_liters", 28.0)),
        efficiency_km_per_liter=float(defaults.get("efficiency_km_per_liter", 10.0)),
        graph=graph,
    )


def load_real_instances(instances_dir: str | Path) -> list[RealRouteInstance]:
    base = Path(instances_dir)
    return [load_real_instance(path) for path in sorted(base.glob("*.json"))]
