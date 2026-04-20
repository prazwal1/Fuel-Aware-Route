# Fuel-Aware Route Optimization on Thailand Road Networks

This repository contains the implementation, experiment data, analysis assets, and final report for the ADA project on fuel-aware route optimization.

The project studies routing when fuel prices vary across stations and the driver can choose both where to stop and how much fuel to buy. The repository includes:

- core algorithms in `src/ada_route_opt`
- automated experiments in `scripts`
- correctness tests in `tests`
- real-route and synthetic datasets in `data` and `results`
- the canonical final report in `final-report`

## Project Layout

The repository is organized around these folders:

```text
src/                    Python package with graph and algorithm implementations
scripts/                Experiment runners and analysis scripts
tests/                  Unit tests
configs/                Experiment configuration files
data/                   Input datasets, including real-route corridor data
results/                Processed experiment outputs and report-ready assets
final-report/           Final LaTeX report source and compiled PDF
```

The latest report to use is:

- `final-report/final-report.tex`
- `final-report/final-report.pdf`

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
```

On Windows PowerShell, use `.venv\Scripts\Activate.ps1` instead of the `source` command.

## Implemented Algorithms

- State-Expanded Dijkstra
- Greedy Refuel baseline
- Dynamic Programming
- Standard A*
- RF-A*
- PF-A*

## Environment Setup Details

Tested with Python 3.11+.

Create an environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

## Tests

Run the test suite after installing dependencies:

```bash
pytest -q
```

## Main Experiment Workflows

Run the synthetic experiment sweep:

```bash
python scripts/run_all_experiments.py --output results
```

Run the real-route experiment sweep:

```powershell
.\scripts\run_windows_real_experiments.ps1 -InstancesDir data/real_routes/generated -Runs 10000 -Warmups 200 -Output results_real -PurchaseModel both
```

Analyze real-route results into report assets:

```powershell
.venv\Scripts\python.exe scripts\analyze_real_results.py --input real_route_results.csv --instances-dir data/real_routes/generated --output-dir results/report_assets/exp6_real_routes
```

## Rebuild The Final Report

From `final-report`:

```powershell
pdflatex -interaction=nonstopmode final-report.tex
biber final-report
pdflatex -interaction=nonstopmode final-report.tex
pdflatex -interaction=nonstopmode final-report.tex
```

## Notes

- `results/report_assets` contains the tables and figures used in the final report.
- `real_route_results.csv` is the full Experiment 6 benchmark output.
- `data/real_routes/generated` contains the generated corridor instances used by the real-route experiments.
