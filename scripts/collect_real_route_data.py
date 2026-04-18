from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import networkx as nx
import pandas as pd

try:
    import osmnx as ox
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise SystemExit(
        "osmnx is required for real-route collection. Install project dependencies first."
    ) from exc

from shapely.geometry import Point


@dataclass(frozen=True)
class CorridorConfig:
    instance_id: str
    route_name: str
    source_query: str
    target_query: str
    country_query: str
    corridor_buffer_km: float
    route_buffer_km: float
    tank_liters: float
    initial_fuel_liters: float
    efficiency_km_per_liter: float
    default_station_price: float
    destination_price: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect OSM road and fuel-station data for Experiment 6 corridor instances."
    )
    parser.add_argument(
        "--config",
        default="data/real_routes/corridors.example.json",
        help="JSON file containing one or more corridor definitions.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/real_routes/generated",
        help="Directory to write collected route-instance JSON files.",
    )
    parser.add_argument(
        "--raw-dir",
        default="data/real_routes/raw",
        help="Directory to write raw station CSVs and route metadata for inspection.",
    )
    parser.add_argument(
        "--station-price-csv",
        default="",
        help=(
            "Optional CSV with station prices. Expected columns: osm_type, osm_id, price. "
            "If absent, stations use the corridor default price."
        ),
    )
    parser.add_argument(
        "--instance-id",
        default="",
        help="If provided, collect only the matching corridor instance.",
    )
    return parser.parse_args()


def load_corridors(path: Path) -> list[CorridorConfig]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    corridors = []
    for item in payload["corridors"]:
        corridors.append(
            CorridorConfig(
                instance_id=item["instance_id"],
                route_name=item["route_name"],
                source_query=item["source_query"],
                target_query=item["target_query"],
                country_query=item.get("country_query", "Thailand"),
                corridor_buffer_km=float(item.get("corridor_buffer_km", 25.0)),
                route_buffer_km=float(item.get("route_buffer_km", 10.0)),
                tank_liters=float(item.get("tank_liters", 40.0)),
                initial_fuel_liters=float(item.get("initial_fuel_liters", 28.0)),
                efficiency_km_per_liter=float(item.get("efficiency_km_per_liter", 10.0)),
                default_station_price=float(item.get("default_station_price", 36.0)),
                destination_price=float(item.get("destination_price", 999.0)),
            )
        )
    return corridors


def load_station_prices(path: str) -> dict[tuple[str, str], float]:
    if not path:
        return {}
    frame = pd.read_csv(path, dtype={"osm_type": str, "osm_id": str})
    required = {"osm_type", "osm_id", "price"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required price CSV columns: {sorted(missing)}")
    return {
        (row.osm_type, row.osm_id): float(row.price)
        for row in frame.itertuples(index=False)
    }


def geocode_point(query: str) -> tuple[float, float]:
    lat, lon = ox.geocode(query)
    return float(lat), float(lon)


def build_corridor_polygon(source_latlon: tuple[float, float], target_latlon: tuple[float, float], buffer_km: float):
    padding_deg = buffer_km / 111.0
    return ox.utils_geo.bbox_to_poly(
        north=max(source_latlon[0], target_latlon[0]) + padding_deg,
        south=min(source_latlon[0], target_latlon[0]) - padding_deg,
        east=max(source_latlon[1], target_latlon[1]) + padding_deg,
        west=min(source_latlon[1], target_latlon[1]) - padding_deg,
    )


def add_path_endpoint(payload_stations: list[dict[str, object]], node_id: str, point: tuple[float, float], price: float) -> None:
    payload_stations.append(
        {
            "node_id": node_id,
            "price": price,
            "lat": point[0],
            "lon": point[1],
        }
    )


def normalize_station_rows(stations_gdf: pd.DataFrame, price_lookup: dict[tuple[str, str], float], default_price: float) -> pd.DataFrame:
    frame = stations_gdf.copy()
    frame = frame.reset_index()

    if "element_type" in frame.columns:
        frame["osm_type"] = frame["element_type"].astype(str)
    elif "index" in frame.columns:
        frame["osm_type"] = frame["index"].astype(str)
    else:
        frame["osm_type"] = "node"

    if "osmid" in frame.columns:
        frame["osm_id"] = frame["osmid"].astype(str)
    elif "id" in frame.columns:
        frame["osm_id"] = frame["id"].astype(str)
    else:
        frame["osm_id"] = frame.index.astype(str)

    frame["price"] = [
        price_lookup.get((row.osm_type, row.osm_id), default_price)
        for row in frame.itertuples(index=False)
    ]
    frame["name"] = frame.get("name", pd.Series([""] * len(frame))).fillna("")
    return frame


def route_geometry(graph: nx.MultiDiGraph, source_node: int, target_node: int):
    route = nx.shortest_path(graph, source=source_node, target=target_node, weight="length")
    gdf = ox.routing.route_to_gdf(graph, route, weight="length")
    return route, gdf.union_all()


def station_within_route_buffer(
    point_lat: float,
    point_lon: float,
    route_geom,
    route_buffer_km: float,
) -> bool:
    point = Point(point_lon, point_lat)
    buffer_deg = route_buffer_km / 111.0
    return route_geom.distance(point) <= buffer_deg


def build_instance_payload(
    corridor: CorridorConfig,
    station_rows: pd.DataFrame,
    graph: nx.MultiDiGraph,
    source_point: tuple[float, float],
    target_point: tuple[float, float],
    source_node: int,
    target_node: int,
) -> dict[str, object]:
    max_leg_km = corridor.tank_liters * corridor.efficiency_km_per_liter
    payload_stations: list[dict[str, object]] = []
    payload_edges: list[dict[str, object]] = []

    add_path_endpoint(payload_stations, "SOURCE", source_point, corridor.default_station_price)
    add_path_endpoint(payload_stations, "TARGET", target_point, corridor.destination_price)

    station_meta: list[tuple[str, int]] = [("SOURCE", source_node), ("TARGET", target_node)]
    for row in station_rows.itertuples(index=False):
        node_id = f"{row.osm_type}_{row.osm_id}"
        payload_stations.append(
            {
                "node_id": node_id,
                "price": float(row.price),
                "lat": float(row.geometry.y),
                "lon": float(row.geometry.x),
                "name": row.name,
                "osm_type": row.osm_type,
                "osm_id": row.osm_id,
            }
        )
        nearest_node = ox.distance.nearest_nodes(graph, X=float(row.geometry.x), Y=float(row.geometry.y))
        station_meta.append((node_id, int(nearest_node)))

    seen_edges: set[tuple[str, str]] = set()
    for from_id, from_node in station_meta:
        lengths = nx.single_source_dijkstra_path_length(graph, from_node, cutoff=max_leg_km * 1000.0, weight="length")
        for to_id, to_node in station_meta:
            if from_id == to_id:
                continue
            if to_node not in lengths:
                continue
            edge_key = (from_id, to_id)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            payload_edges.append(
                {
                    "from_node": from_id,
                    "to_node": to_id,
                    "distance_km": round(float(lengths[to_node]) / 1000.0, 3),
                }
            )

    return {
        "instance_id": corridor.instance_id,
        "route_name": corridor.route_name,
        "source": "SOURCE",
        "target": "TARGET",
        "vehicle": {
            "tank_liters": corridor.tank_liters,
            "initial_fuel_liters": corridor.initial_fuel_liters,
            "efficiency_km_per_liter": corridor.efficiency_km_per_liter,
        },
        "stations": payload_stations,
        "edges": payload_edges,
    }


def collect_corridor(
    corridor: CorridorConfig,
    output_dir: Path,
    raw_dir: Path,
    price_lookup: dict[tuple[str, str], float],
) -> None:
    source_query = f"{corridor.source_query}, {corridor.country_query}"
    target_query = f"{corridor.target_query}, {corridor.country_query}"

    source_point = geocode_point(source_query)
    target_point = geocode_point(target_query)
    polygon = build_corridor_polygon(source_point, target_point, corridor.corridor_buffer_km)

    graph = ox.graph_from_polygon(polygon, network_type="drive", simplify=True)
    stations = ox.features_from_polygon(polygon, tags={"amenity": "fuel"})
    stations = normalize_station_rows(stations, price_lookup, corridor.default_station_price)

    source_node = ox.distance.nearest_nodes(graph, X=source_point[1], Y=source_point[0])
    target_node = ox.distance.nearest_nodes(graph, X=target_point[1], Y=target_point[0])
    _route_nodes, route_geom = route_geometry(graph, source_node, target_node)

    stations = stations[
        stations.apply(
            lambda row: station_within_route_buffer(
                point_lat=float(row.geometry.y),
                point_lon=float(row.geometry.x),
                route_geom=route_geom,
                route_buffer_km=corridor.route_buffer_km,
            ),
            axis=1,
        )
    ].copy()

    raw_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_csv = raw_dir / f"{corridor.instance_id}_stations.csv"
    stations.assign(
        lat=stations.geometry.y,
        lon=stations.geometry.x,
    ).drop(columns=["geometry"]).to_csv(raw_csv, index=False)

    instance_payload = build_instance_payload(
        corridor=corridor,
        station_rows=stations,
        graph=graph,
        source_point=source_point,
        target_point=target_point,
        source_node=int(source_node),
        target_node=int(target_node),
    )
    instance_path = output_dir / f"{corridor.instance_id}.json"
    instance_path.write_text(json.dumps(instance_payload, indent=2), encoding="utf-8")
    print(
        f"collected route={corridor.instance_id} stations={len(instance_payload['stations'])} "
        f"edges={len(instance_payload['edges'])} -> {instance_path}",
        flush=True,
    )


def main() -> None:
    args = parse_args()
    corridors = load_corridors(Path(args.config))
    if args.instance_id:
        corridors = [corridor for corridor in corridors if corridor.instance_id == args.instance_id]
    if not corridors:
        raise SystemExit("No corridor definitions selected.")

    price_lookup = load_station_prices(args.station_price_csv)
    output_dir = Path(args.output_dir)
    raw_dir = Path(args.raw_dir)

    ox.settings.use_cache = True
    ox.settings.log_console = True

    for corridor in corridors:
        collect_corridor(corridor, output_dir=output_dir, raw_dir=raw_dir, price_lookup=price_lookup)


if __name__ == "__main__":
    main()
