from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - handled at runtime for user convenience
    plt = None


EXPERIMENT_SPECS = {
    "exp1_scalability": {
        "title": "Experiment 1: Scalability",
        "x": "nodes",
        "x_label": "Number of Nodes",
        "facet": None,
        "algorithms": None,
    },
    "exp2_price_variance": {
        "title": "Experiment 2: Price Variance",
        "x": "sigma_pct",
        "x_label": "Fuel Price Variance (%)",
        "facet": None,
        "algorithms": None,
    },
    "exp3_tank_capacity": {
        "title": "Experiment 3: Tank Capacity",
        "x": "tank_liters",
        "x_label": "Tank Capacity (L)",
        "facet": None,
        "algorithms": None,
    },
    "exp4_initial_fuel": {
        "title": "Experiment 4: Initial Fuel",
        "x": "initial_fuel_liters",
        "x_label": "Initial Fuel (L)",
        "facet": None,
        "algorithms": None,
    },
    "exp5_rf_vs_pf": {
        "title": "Experiment 5: RF-A* vs PF-A*",
        "x": "degree",
        "x_label": "Approximate Graph Degree",
        "facet": "sigma_pct",
        "algorithms": ["rf_astar", "pf_astar"],
    },
    "exp7_variable_vs_full_tank": {
        "title": "Experiment 7: Variable Fill vs Full Tank",
        "x": "tank_liters",
        "x_label": "Tank Capacity (L)",
        "facet": "sigma_pct",
        "algorithms": ["dijkstra", "full_tank_only_dijkstra"],
    },
}

METRIC_SPECS = [
    ("mean_runtime_ms", "Runtime (ms)", "runtime"),
    ("mean_expanded_states", "Expanded States", "expanded_states"),
    ("mean_cost", "Mean Cost", "cost"),
    ("feasible_rate_pct", "Feasible Runs (%)", "feasibility"),
]

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate report-ready charts and tables from synthetic_results.csv."
    )
    parser.add_argument(
        "--input",
        default="results/synthetic_results.csv",
        help="Path to the synthetic results CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/report_assets",
        help="Directory to write charts, tables, and markdown summaries.",
    )
    return parser.parse_args()


def load_results(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["feasible"] = df["feasible"].astype(str).str.lower().eq("true")
    numeric_columns = [
        "run",
        "cost",
        "runtime_ms",
        "expanded_states",
        "nodes",
        "degree",
        "sigma_pct",
        "tank_liters",
        "initial_fuel_liters",
        "efficiency_km_per_liter",
        "seed",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["cost"] = df["cost"].replace([np.inf, -np.inf], np.nan)
    return df


def algorithm_sort_key(name: str) -> tuple[int, str]:
    try:
        return (ALGORITHM_ORDER.index(name), name)
    except ValueError:
        return (len(ALGORITHM_ORDER), name)


def format_algorithm(name: str) -> str:
    return ALGORITHM_LABELS.get(name, name)


def summarize_experiment(df: pd.DataFrame, experiment: str) -> pd.DataFrame:
    spec = EXPERIMENT_SPECS[experiment]
    group_columns = ["algorithm", spec["x"]]
    if spec["facet"]:
        group_columns.append(spec["facet"])

    summary = (
        df.groupby(group_columns, dropna=False)
        .agg(
            runs=("run", "count"),
            feasible_runs=("feasible", "sum"),
            feasible_rate_pct=("feasible", lambda s: float(s.mean() * 100.0)),
            mean_runtime_ms=("runtime_ms", "mean"),
            std_runtime_ms=("runtime_ms", "std"),
            median_runtime_ms=("runtime_ms", "median"),
            mean_expanded_states=("expanded_states", "mean"),
            mean_cost=("cost", "mean"),
            median_cost=("cost", "median"),
            min_cost=("cost", "min"),
            max_cost=("cost", "max"),
        )
        .reset_index()
    )

    baseline_columns = [spec["x"]]
    if spec["facet"]:
        baseline_columns.append(spec["facet"])

    best_cost = (
        summary.groupby(baseline_columns, dropna=False)["mean_cost"]
        .min()
        .rename("best_mean_cost")
        .reset_index()
    )
    fastest_runtime = (
        summary.groupby(baseline_columns, dropna=False)["mean_runtime_ms"]
        .min()
        .rename("best_mean_runtime_ms")
        .reset_index()
    )

    summary = summary.merge(best_cost, on=baseline_columns, how="left")
    summary = summary.merge(fastest_runtime, on=baseline_columns, how="left")
    summary["cost_gap_pct_vs_best"] = (
        (summary["mean_cost"] - summary["best_mean_cost"]) / summary["best_mean_cost"] * 100.0
    )
    summary["runtime_gap_pct_vs_fastest"] = (
        (summary["mean_runtime_ms"] - summary["best_mean_runtime_ms"])
        / summary["best_mean_runtime_ms"]
        * 100.0
    )
    summary["algorithm_label"] = summary["algorithm"].map(format_algorithm)
    summary["algorithm_order"] = summary["algorithm"].map(lambda name: algorithm_sort_key(name)[0])
    summary = summary.sort_values(
        by=["algorithm_order", *[column for column in group_columns if column != "algorithm"]],
    ).drop(columns=["algorithm_order"]).reset_index(drop=True)
    return summary


def report_table(summary: pd.DataFrame, experiment: str) -> pd.DataFrame:
    spec = EXPERIMENT_SPECS[experiment]
    columns = ["algorithm_label", spec["x"]]
    rename_map = {
        "algorithm_label": "Algorithm",
        spec["x"]: spec["x_label"],
        "feasible_rate_pct": "Feasible (%)",
        "mean_cost": "Mean Cost",
        "cost_gap_pct_vs_best": "Cost Gap vs Best (%)",
        "mean_runtime_ms": "Mean Runtime (ms)",
        "std_runtime_ms": "Runtime Std (ms)",
        "mean_expanded_states": "Mean Expanded States",
    }
    if spec["facet"]:
        columns.append(spec["facet"])
        rename_map[spec["facet"]] = spec["facet"].replace("_", " ").title()

    columns.extend(
        [
            "feasible_rate_pct",
            "mean_cost",
            "cost_gap_pct_vs_best",
            "mean_runtime_ms",
            "std_runtime_ms",
            "mean_expanded_states",
        ]
    )
    table = summary[columns].rename(columns=rename_map).copy()
    numeric_columns = table.select_dtypes(include=["number"]).columns
    table[numeric_columns] = table[numeric_columns].round(2)
    return table


def insight_lines(summary: pd.DataFrame, experiment: str) -> list[str]:
    spec = EXPERIMENT_SPECS[experiment]
    lines = [f"## {spec['title']}"]

    feasible_summary = summary[summary["feasible_rate_pct"] > 0].copy()
    if feasible_summary.empty:
        lines.append("- No algorithm produced a feasible solution in this experiment.")
        return lines

    runtime_winner = feasible_summary.loc[feasible_summary["mean_runtime_ms"].idxmin()]
    cost_winner = feasible_summary.loc[feasible_summary["mean_cost"].idxmin()]
    reliability_winner = summary.loc[summary["feasible_rate_pct"].idxmax()]

    lines.append(
        "- Fastest feasible algorithm overall: "
        f"{format_algorithm(runtime_winner['algorithm'])} "
        f"with mean runtime {runtime_winner['mean_runtime_ms']:.2f} ms."
    )
    lines.append(
        "- Lowest mean cost overall: "
        f"{format_algorithm(cost_winner['algorithm'])} "
        f"with mean cost {cost_winner['mean_cost']:.2f}."
    )
    lines.append(
        "- Highest feasibility rate: "
        f"{format_algorithm(reliability_winner['algorithm'])} "
        f"at {reliability_winner['feasible_rate_pct']:.1f}%."
    )

    failures = summary[summary["feasible_rate_pct"] < 100.0]
    if not failures.empty:
        failure_names = ", ".join(sorted({format_algorithm(name) for name in failures["algorithm"]}))
        lines.append(f"- Algorithms with incomplete feasibility in this experiment: {failure_names}.")

    if spec["facet"]:
        for facet_value in sorted(summary[spec["facet"]].dropna().unique()):
            facet_df = feasible_summary[feasible_summary[spec["facet"]] == facet_value]
            if facet_df.empty:
                continue
            facet_winner = facet_df.loc[facet_df["mean_runtime_ms"].idxmin()]
            lines.append(
                f"- At {spec['facet'].replace('_', ' ')}={facet_value}, "
                f"{format_algorithm(facet_winner['algorithm'])} is the fastest feasible method "
                f"at {facet_winner['mean_runtime_ms']:.2f} ms."
            )

    return lines


def write_tables(summary: pd.DataFrame, experiment: str, output_dir: Path) -> None:
    table = report_table(summary, experiment)
    experiment_dir = output_dir / experiment
    experiment_dir.mkdir(parents=True, exist_ok=True)

    csv_path = experiment_dir / f"{experiment}_summary.csv"
    md_path = experiment_dir / f"{experiment}_summary.md"
    tex_path = experiment_dir / f"{experiment}_summary.tex"

    table.to_csv(csv_path, index=False)
    md_path.write_text(to_markdown_table(table), encoding="utf-8")
    tex_path.write_text(to_latex_table(table), encoding="utf-8")


def to_markdown_table(table: pd.DataFrame) -> str:
    headers = [str(column) for column in table.columns]
    rows = [[str(value) for value in row] for row in table.astype(object).fillna("").values.tolist()]
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def format_row(values: list[str]) -> str:
        padded = [value.ljust(widths[index]) for index, value in enumerate(values)]
        return "| " + " | ".join(padded) + " |"

    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    lines = [format_row(headers), separator]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines) + "\n"


def to_latex_table(table: pd.DataFrame) -> str:
    headers = [escape_latex(str(column)) for column in table.columns]
    rows = [[escape_latex(str(value)) for value in row] for row in table.astype(object).fillna("").values.tolist()]
    column_spec = "l" + "r" * (len(headers) - 1)
    lines = [f"\\begin{{tabular}}{{{column_spec}}}", "\\hline"]
    lines.append(" & ".join(headers) + r" \\")
    lines.append("\\hline")
    for row in rows:
        lines.append(" & ".join(row) + r" \\")
    lines.extend(["\\hline", "\\end{tabular}"])
    return "\n".join(lines) + "\n"


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


def sanitize_filename(value: object) -> str:
    text = str(value)
    return text.replace(".", "_").replace("%", "pct").replace(" ", "_")


def plot_metric(
    summary: pd.DataFrame,
    experiment: str,
    metric_column: str,
    metric_label: str,
    metric_slug: str,
    output_dir: Path,
) -> list[Path]:
    if plt is None:
        return []

    spec = EXPERIMENT_SPECS[experiment]
    experiment_dir = output_dir / experiment
    experiment_dir.mkdir(parents=True, exist_ok=True)
    chart_paths: list[Path] = []

    facet_values = [None]
    if spec["facet"]:
        facet_values = sorted(summary[spec["facet"]].dropna().unique())

    for facet_value in facet_values:
        plot_df = summary.copy()
        facet_suffix = ""
        facet_title = ""
        if spec["facet"]:
            plot_df = plot_df[plot_df[spec["facet"]] == facet_value]
            facet_suffix = f"_{spec['facet']}_{sanitize_filename(facet_value)}"
            facet_title = f" ({spec['facet'].replace('_', ' ')}={facet_value})"

        if plot_df.empty:
            continue

        fig, ax = plt.subplots(figsize=(9, 5.5))
        for algorithm in sorted(plot_df["algorithm"].unique(), key=algorithm_sort_key):
            algo_df = plot_df[plot_df["algorithm"] == algorithm].sort_values(spec["x"])
            ax.plot(
                algo_df[spec["x"]],
                algo_df[metric_column],
                marker="o",
                linewidth=2,
                label=format_algorithm(algorithm),
            )

        ax.set_title(f"{spec['title']}: {metric_label}{facet_title}")
        ax.set_xlabel(spec["x_label"])
        ax.set_ylabel(metric_label)
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
        ax.legend(loc="best")
        fig.tight_layout()

        chart_path = experiment_dir / f"{experiment}_{metric_slug}{facet_suffix}.png"
        fig.savefig(chart_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        chart_paths.append(chart_path)

    return chart_paths


def write_overview(
    summaries: dict[str, pd.DataFrame],
    all_chart_paths: dict[str, list[Path]],
    output_dir: Path,
) -> None:
    lines = ["# Synthetic Experiment Results Overview", ""]
    for experiment in EXPERIMENT_SPECS:
        if experiment not in summaries:
            continue
        lines.extend(insight_lines(summaries[experiment], experiment))
        chart_paths = all_chart_paths.get(experiment, [])
        if chart_paths:
            lines.append("- Generated charts:")
            for path in chart_paths:
                lines.append(f"  - `{path.as_posix()}`")
        lines.append("")

    if plt is None:
        lines.append(
            "Charts were skipped because `matplotlib` is not installed in the active environment."
        )

    (output_dir / "synthetic_results_overview.md").write_text(
        "\n".join(lines).strip() + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_results(input_path)
    summaries: dict[str, pd.DataFrame] = {}
    all_chart_paths: dict[str, list[Path]] = {}

    for experiment in EXPERIMENT_SPECS:
        experiment_df = df[df["experiment"] == experiment].copy()
        if experiment_df.empty:
            continue

        summary = summarize_experiment(experiment_df, experiment)
        summaries[experiment] = summary
        write_tables(summary, experiment, output_dir)

        chart_paths: list[Path] = []
        for metric_column, metric_label, metric_slug in METRIC_SPECS:
            chart_paths.extend(
                plot_metric(
                    summary=summary,
                    experiment=experiment,
                    metric_column=metric_column,
                    metric_label=metric_label,
                    metric_slug=metric_slug,
                    output_dir=output_dir,
                )
            )
        all_chart_paths[experiment] = chart_paths

    write_overview(summaries, all_chart_paths, output_dir)
    print(f"Report assets written to {output_dir}")


if __name__ == "__main__":
    main()
