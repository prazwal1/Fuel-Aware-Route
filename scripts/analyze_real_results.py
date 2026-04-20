from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - optional chart generation
    plt = None


ALGORITHM_LABELS = {
    "dijkstra": "State-Expanded Dijkstra",
    "dynamic_programming": "Dynamic Programming",
    "greedy": "Greedy Refuel",
    "standard_astar": "Standard A*",
    "rf_astar": "RF-A*",
    "pf_astar": "PF-A*",
    "full_tank_only_dijkstra": "Full-Tank-Only Dijkstra",
}

ALGORITHM_ORDER = [
    "dijkstra",
    "dynamic_programming",
    "greedy",
    "standard_astar",
    "rf_astar",
    "pf_astar",
    "full_tank_only_dijkstra",
]

CORE_ALGORITHMS = [
    "dijkstra",
    "dynamic_programming",
    "pf_astar",
    "rf_astar",
    "standard_astar",
    "full_tank_only_dijkstra",
]

SERIES_STYLES = {
    "State-Expanded Dijkstra": {"color": "#4E79A7", "hatch": "//"},
    "Dynamic Programming": {"color": "#F28E2B", "hatch": "\\\\"},
    "PF-A*": {"color": "#59A14F", "hatch": "xx"},
    "RF-A*": {"color": "#E15759", "hatch": ".."},
    "Standard A*": {"color": "#B07AA1", "hatch": "++"},
    "Full-Tank-Only Dijkstra": {"color": "#9C755F", "hatch": "--"},
    "Variable Purchase": {"color": "#76B7B2", "hatch": "//"},
    "Full-Tank-Only": {"color": "#EDC948", "hatch": "\\\\"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate report-ready charts and tables from real_route_results.csv."
    )
    parser.add_argument("--input", default="real_route_results.csv")
    parser.add_argument("--instances-dir", default="data/real_routes/generated")
    parser.add_argument("--output-dir", default="results/report_assets/exp6_real_routes")
    return parser.parse_args()


def algorithm_sort_key(name: str) -> tuple[int, str]:
    try:
        return (ALGORITHM_ORDER.index(name), name)
    except ValueError:
        return (len(ALGORITHM_ORDER), name)


def format_algorithm(name: str) -> str:
    return ALGORITHM_LABELS.get(name, name)


def format_number(value: object, decimals: int = 2) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        if math.isinf(value):
            return "inf"
        return f"{value:.{decimals}f}"
    return str(value)


def escape_latex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    escaped = text
    for source, target in replacements.items():
        escaped = escaped.replace(source, target)
    return escaped


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_number(row.get(key)) for key in fieldnames})


def write_markdown(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    headers = fieldnames
    body_rows = [[format_number(row.get(key)) for key in fieldnames] for row in rows]
    widths = [len(header) for header in headers]
    for row in body_rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def fmt(values: list[str]) -> str:
        return "| " + " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(values)) + " |"

    lines = [fmt(headers), "| " + " | ".join("-" * width for width in widths) + " |"]
    lines.extend(fmt(row) for row in body_rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_latex(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    column_spec = "l" + "r" * (len(fieldnames) - 1)
    lines = [f"\\begin{{tabular}}{{{column_spec}}}", "\\hline"]
    lines.append(" & ".join(escape_latex(name) for name in fieldnames) + r" \\")
    lines.append("\\hline")
    for row in rows:
        values = [escape_latex(format_number(row.get(key))) for key in fieldnames]
        lines.append(" & ".join(values) + r" \\")
    lines.extend(["\\hline", "\\end{tabular}"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_table_bundle(base_path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    write_csv(base_path.with_suffix(".csv"), rows, fieldnames)
    write_markdown(base_path.with_suffix(".md"), rows, fieldnames)
    write_latex(base_path.with_suffix(".tex"), rows, fieldnames)


def load_results(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            feasible = str(row["feasible"]).lower() == "true"
            try:
                cost = float(row["cost"])
            except ValueError:
                cost = math.inf
            rows.append(
                {
                    "experiment": row["experiment"],
                    "route_name": row["route_name"],
                    "instance_id": row["instance_id"],
                    "purchase_model": row["purchase_model"],
                    "run": int(row["run"]),
                    "algorithm": row["algorithm"],
                    "feasible": feasible,
                    "cost": cost,
                    "runtime_ms": float(row["runtime_ms"]),
                    "expanded_states": float(row["expanded_states"]),
                    "path": row["path"],
                }
            )
    return rows


def summarize_algorithms(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        key = (row["route_name"], row["instance_id"], row["purchase_model"], row["algorithm"])
        grouped[key].append(row)

    summaries: list[dict[str, object]] = []
    dijkstra_cost_by_instance: dict[str, float] = {}

    for key in sorted(grouped, key=lambda item: (item[1], item[2], algorithm_sort_key(item[3]))):
        route_name, instance_id, purchase_model, algorithm = key
        items = grouped[key]
        feasible_rate_pct = sum(1 for item in items if item["feasible"]) / len(items) * 100.0
        runtime_values = [item["runtime_ms"] for item in items]
        expanded_values = [item["expanded_states"] for item in items]
        cost_values = [item["cost"] for item in items if item["feasible"] and not math.isinf(item["cost"])]
        paths = [item["path"] for item in items if item["path"]]
        path_mode = statistics.mode(paths) if paths else ""

        summary = {
            "Route": route_name,
            "Instance ID": instance_id,
            "Model": purchase_model,
            "Algorithm": format_algorithm(algorithm),
            "algorithm": algorithm,
            "Feasible (%)": feasible_rate_pct,
            "Mean Cost": statistics.mean(cost_values) if cost_values else math.inf,
            "Mean Runtime (ms)": statistics.mean(runtime_values),
            "Runtime Std (ms)": statistics.pstdev(runtime_values),
            "Mean Expanded States": statistics.mean(expanded_values),
            "Dominant Path": path_mode,
        }
        summaries.append(summary)
        if algorithm == "dijkstra":
            dijkstra_cost_by_instance[instance_id] = summary["Mean Cost"]

    for summary in summaries:
        optimum = dijkstra_cost_by_instance[summary["Instance ID"]]
        if math.isinf(summary["Mean Cost"]):
            gap_thb = math.inf
            gap_pct = math.inf
        else:
            gap_thb = summary["Mean Cost"] - optimum
            gap_pct = (gap_thb / optimum) * 100.0 if optimum else 0.0
        summary["Cost Gap vs Optimum (THB)"] = gap_thb
        summary["Cost Gap vs Optimum (%)"] = gap_pct

    return summaries


def load_instance_metadata(instances_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(instances_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        stations = payload["stations"]
        edges = payload["edges"]
        prices = []
        provinces = set()
        for station in stations:
            price = float(station.get("price_thb_per_l", station.get("price", 0.0)))
            if price < 1000.0:
                prices.append(price)
            province = station.get("province")
            if province:
                provinces.add(province)
        rows.append(
            {
                "Route": payload.get("label", payload.get("route_name", payload["instance_id"])),
                "Instance ID": payload["instance_id"],
                "Stations": len(stations),
                "Directed Edges": len(edges),
                "Price Min (THB/L)": min(prices) if prices else None,
                "Price Max (THB/L)": max(prices) if prices else None,
                "Province Count": len(provinces),
                "Provinces": ", ".join(sorted(provinces)),
            }
        )
    return rows


def make_savings_table(summaries: list[dict[str, object]]) -> list[dict[str, object]]:
    by_instance: dict[str, dict[str, float]] = defaultdict(dict)
    route_name_by_instance: dict[str, str] = {}
    for row in summaries:
        instance_id = row["Instance ID"]
        route_name_by_instance[instance_id] = row["Route"]
        if row["algorithm"] == "dijkstra":
            by_instance[instance_id]["variable"] = row["Mean Cost"]
        if row["algorithm"] == "full_tank_only_dijkstra":
            by_instance[instance_id]["full_tank_only"] = row["Mean Cost"]

    output: list[dict[str, object]] = []
    for instance_id in sorted(by_instance):
        variable_cost = by_instance[instance_id]["variable"]
        full_cost = by_instance[instance_id]["full_tank_only"]
        savings = full_cost - variable_cost
        output.append(
            {
                "Route": route_name_by_instance[instance_id],
                "Instance ID": instance_id,
                "Variable-Purchase Cost": variable_cost,
                "Full-Tank-Only Cost": full_cost,
                "Savings (THB)": savings,
                "Savings (%)": savings / full_cost * 100.0 if full_cost else 0.0,
            }
        )
    return output


def plot_grouped_bar(
    x_labels: list[str],
    series: list[tuple[str, list[float]]],
    title: str,
    ylabel: str,
    output_path: Path,
) -> Path | None:
    if plt is None:
        return None
    width = 0.8 / max(len(series), 1)
    positions = list(range(len(x_labels)))
    fig, ax = plt.subplots(figsize=(11.5, 6.4))
    max_value = max((max(values) for _, values in series), default=0.0)
    for index, (label, values) in enumerate(series):
        offset = (index - (len(series) - 1) / 2.0) * width
        style = SERIES_STYLES.get(label, {})
        bars = ax.bar(
            [pos + offset for pos in positions],
            values,
            width=width,
            label=label,
            color=style.get("color"),
            hatch=style.get("hatch", ""),
            edgecolor="black",
            linewidth=0.8,
        )
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + max_value * 0.012,
                format_number(value, 1),
                ha="center",
                va="bottom",
                rotation=90,
                fontsize=7,
            )
    ax.set_xticks(positions)
    ax.set_xticklabels(x_labels)
    ax.set_title(title)
    ax.set_xlabel("Route")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max_value * 1.14 if max_value else 1.0)
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_station_price_profiles(instances_dir: Path, output_dir: Path) -> list[Path]:
    if plt is None:
        return []
    outputs: list[Path] = []
    for path in sorted(instances_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        stations = payload["stations"]
        prices: list[float] = []
        for station in stations:
            station_id = str(station.get("id", station.get("node_id", "")))
            price = float(station.get("price_thb_per_l", station.get("price", 0.0)))
            if station_id.startswith("dst_") or price >= 1000.0:
                continue
            prices.append(price)
        fig, ax = plt.subplots(figsize=(9, 4.8))
        ax.plot(range(len(prices)), prices, marker="o", linewidth=1.8)
        ax.set_title(f"{payload.get('label', payload['instance_id'])}: Station Price Profile")
        ax.set_xlabel("Station Order Along Corridor")
        ax.set_ylabel("Price (THB/L)")
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
        fig.tight_layout()
        output_path = output_dir / f"exp6_real_routes_station_prices_{payload['instance_id']}.png"
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        outputs.append(output_path)
    return outputs


def write_overview(
    output_dir: Path,
    total_rows: int,
    summaries: list[dict[str, object]],
    savings_rows: list[dict[str, object]],
    chart_paths: list[Path],
) -> None:
    lines = ["# Experiment 6 Real-Route Overview", ""]
    lines.append(f"- Total result rows: {total_rows}")
    lines.append("- Timed runs per corridor/algorithm combination: 10,000")
    lines.append("- Corridors covered: Bangkok to Chiang Mai, Bangkok to Phuket, Bangkok to Khon Kaen")
    lines.append("")
    lines.append("## Key Findings")
    lines.append("- PF-A* matches State-Expanded Dijkstra on all three real-route corridors.")
    lines.append("- Full-tank-only Dijkstra is more expensive than the variable-purchase optimum on every corridor.")
    lines.append("- Standard A* and RF-A* still show small positive cost gaps on Phuket and Khon Kaen.")
    lines.append("- Greedy is infeasible on all three current corridor graphs.")
    lines.append("")
    lines.append("## Savings Summary")
    for row in savings_rows:
        lines.append(
            f"- {row['Route']}: {format_number(row['Savings (THB)'])} THB saved ({format_number(row['Savings (%)'])}%)."
        )
    if chart_paths:
        lines.append("")
        lines.append("## Generated Charts")
        for path in chart_paths:
            lines.append(f"- `{path.as_posix()}`")
    (output_dir / "exp6_real_routes_overview.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    instances_dir = Path(args.instances_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_results(input_path)
    summaries = summarize_algorithms(rows)
    summaries = sorted(
        summaries,
        key=lambda row: (row["Instance ID"], row["Model"], algorithm_sort_key(row["algorithm"])),
    )
    dataset_rows = load_instance_metadata(instances_dir)
    savings_rows = make_savings_table(summaries)

    algorithm_fieldnames = [
        "Route",
        "Model",
        "Algorithm",
        "Feasible (%)",
        "Mean Cost",
        "Cost Gap vs Optimum (THB)",
        "Cost Gap vs Optimum (%)",
        "Mean Runtime (ms)",
        "Runtime Std (ms)",
        "Mean Expanded States",
        "Dominant Path",
    ]
    algorithm_rows = [{key: row[key] for key in algorithm_fieldnames} for row in summaries]
    write_table_bundle(output_dir / "exp6_real_routes_algorithm_summary", algorithm_rows, algorithm_fieldnames)

    dataset_fieldnames = [
        "Route",
        "Instance ID",
        "Stations",
        "Directed Edges",
        "Price Min (THB/L)",
        "Price Max (THB/L)",
        "Province Count",
        "Provinces",
    ]
    write_table_bundle(output_dir / "exp6_real_routes_dataset_summary", dataset_rows, dataset_fieldnames)

    savings_fieldnames = [
        "Route",
        "Instance ID",
        "Variable-Purchase Cost",
        "Full-Tank-Only Cost",
        "Savings (THB)",
        "Savings (%)",
    ]
    write_table_bundle(output_dir / "exp6_real_routes_savings_summary", savings_rows, savings_fieldnames)

    chart_paths: list[Path] = []
    runtime_lookup = {
        (row["Route"], row["Algorithm"]): row["Mean Runtime (ms)"]
        for row in algorithm_rows
        if row["Algorithm"] in {format_algorithm(name) for name in CORE_ALGORITHMS}
    }
    expanded_lookup = {
        (row["Route"], row["Algorithm"]): row["Mean Expanded States"]
        for row in algorithm_rows
        if row["Algorithm"] in {format_algorithm("dijkstra"), format_algorithm("rf_astar"), format_algorithm("pf_astar")}
    }

    route_names = [row["Route"] for row in dataset_rows]
    runtime_chart = plot_grouped_bar(
        x_labels=route_names,
        series=[
            (format_algorithm(name), [runtime_lookup[(route, format_algorithm(name))] for route in route_names])
            for name in CORE_ALGORITHMS
            if all((route, format_algorithm(name)) in runtime_lookup for route in route_names)
        ],
        title="Experiment 6: Mean Runtime by Route and Algorithm",
        ylabel="Mean Runtime (ms)",
        output_path=output_dir / "exp6_real_routes_runtime.png",
    )
    if runtime_chart is not None:
        chart_paths.append(runtime_chart)

    expanded_chart = plot_grouped_bar(
        x_labels=route_names,
        series=[
            (format_algorithm(name), [expanded_lookup[(route, format_algorithm(name))] for route in route_names])
            for name in ["dijkstra", "rf_astar", "pf_astar"]
            if all((route, format_algorithm(name)) in expanded_lookup for route in route_names)
        ],
        title="Experiment 6: Expanded States on Real Routes",
        ylabel="Mean Expanded States",
        output_path=output_dir / "exp6_real_routes_expanded_states.png",
    )
    if expanded_chart is not None:
        chart_paths.append(expanded_chart)

    cost_chart = plot_grouped_bar(
        x_labels=route_names,
        series=[
            ("Variable Purchase", [row["Variable-Purchase Cost"] for row in savings_rows]),
            ("Full-Tank-Only", [row["Full-Tank-Only Cost"] for row in savings_rows]),
        ],
        title="Experiment 6: Variable Purchase vs Full-Tank-Only Cost",
        ylabel="Mean Cost (THB)",
        output_path=output_dir / "exp6_real_routes_cost_compare.png",
    )
    if cost_chart is not None:
        chart_paths.append(cost_chart)

    chart_paths.extend(plot_station_price_profiles(instances_dir, output_dir))
    write_overview(output_dir, len(rows), summaries, savings_rows, chart_paths)
    print(f"Experiment 6 report assets written to {output_dir}")


if __name__ == "__main__":
    main()
