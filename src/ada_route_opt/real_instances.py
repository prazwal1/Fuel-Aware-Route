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


def _station_node_id(station: dict[str, object]) -> str:
    node_id = station.get("node_id", station.get("id"))
    if node_id is None:
        raise KeyError("Station entry is missing both 'node_id' and 'id'.")
    return str(node_id)


def _station_price(station: dict[str, object]) -> float:
    if "price" in station:
        return float(station["price"])
    if "price_thb_per_l" in station:
        return float(station["price_thb_per_l"])
    raise KeyError("Station entry is missing both 'price' and 'price_thb_per_l'.")


def _edge_from_node(edge: dict[str, object]) -> str:
    from_node = edge.get("from_node", edge.get("source"))
    if from_node is None:
        raise KeyError("Edge entry is missing both 'from_node' and 'source'.")
    return str(from_node)


def _edge_to_node(edge: dict[str, object]) -> str:
    to_node = edge.get("to_node", edge.get("target"))
    if to_node is None:
        raise KeyError("Edge entry is missing both 'to_node' and 'target'.")
    return str(to_node)


def _vehicle_value(vehicle: dict[str, object], *keys: str, default: float) -> float:
    for key in keys:
        if key in vehicle:
            return float(vehicle[key])
    return default


def load_real_instance(path: str | Path) -> RealRouteInstance:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    # JSON files may come from different collection scripts, so helper accessors normalize keys.
    graph = FuelGraph()
    for station in payload["stations"]:
        graph.add_station(
            _station_node_id(station),
            _station_price(station),
            lat=station.get("lat"),
            lon=station.get("lon"),
        )

    for edge in payload["edges"]:
        # Edges are stored as directed travel segments between station nodes.
        graph.add_edge(
            _edge_from_node(edge),
            _edge_to_node(edge),
            float(edge["distance_km"]),
        )

    defaults = payload.get("vehicle", {})
    return RealRouteInstance(
        instance_id=payload["instance_id"],
        route_name=payload.get("route_name", payload.get("label", payload["instance_id"])),
        source=str(payload["source"]),
        target=str(payload["target"]),
        tank_liters=_vehicle_value(defaults, "tank_liters", "tank_capacity_l", default=40.0),
        initial_fuel_liters=_vehicle_value(defaults, "initial_fuel_liters", "initial_fuel_l", default=28.0),
        efficiency_km_per_liter=_vehicle_value(
            defaults,
            "efficiency_km_per_liter",
            "efficiency_km_per_l",
            default=10.0,
        ),
        graph=graph,
    )


def load_real_instances(instances_dir: str | Path) -> list[RealRouteInstance]:
    base = Path(instances_dir)
    return [load_real_instance(path) for path in sorted(base.glob("*.json"))]
