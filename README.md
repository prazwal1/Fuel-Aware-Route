# Fuel-Aware Route Optimization on Thailand Road Networks

This repository is a runnable Python scaffold for the ADA project proposal in `ADA-Proposal.pdf`.
It implements the core fuel-aware route optimization algorithms and benchmarking harness:

- State-expanded Dijkstra
- Greedy refueling baseline
- Dynamic programming baseline
- Standard A*
- Refuel A* (RF-A*)
- Partial-Fill A* (PF-A*)
- Synthetic graph generation
- Benchmark scripts for the proposed experiments
- Unit tests for correctness checks

## VM Setup

Tested target from the proposal: Ubuntu 22.04 LTS, Python 3.11.

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Quick Correctness Run

```bash
source .venv/bin/activate
pytest -q
```

## Run a Small Benchmark

```bash
source .venv/bin/activate
python scripts/run_synthetic_experiment.py --nodes 100 --runs 25 --seed 42
```

## Run the Proposal-Style Experiment Sweep

```bash
source .venv/bin/activate
python scripts/run_all_experiments.py --output results
```

The default sweep is intentionally smaller than the proposal's final 10,000 timed runs so you can sanity-check the VM quickly. Increase `--runs` when the code is stable:

```bash
python scripts/run_all_experiments.py --runs 10000 --output results_full
```

## Windows VM Setup With uv

From PowerShell in this project folder:

```powershell
uv python install 3.11
uv venv --python 3.11
uv pip install -r requirements.txt -e .
uv run pytest -q
```

Quick smoke run:

```powershell
.\scripts\run_windows_synthetic_experiments.ps1 -Profile smoke -Runs 10 -Warmups 0 -Output results_smoke
```

Generate charts and report-ready tables from a completed CSV:

```powershell
uv run python scripts/analyze_synthetic_results.py --input results/synthetic_results.csv --output-dir results/report_assets
```

Time-saving 100-run synthetic sweep:

```powershell
.\scripts\run_synthetic_100.ps1
```

Light 10,000-run synthetic sweep designed to finish much faster than the full proposal-scale run:

```powershell
.\scripts\run_windows_synthetic_experiments.ps1 -Profile lite -Runs 10000 -Warmups 0 -Output results_lite_10k -Degree 3
```

If the VM is still slow, reduce only the graph size while keeping 10,000 runs:

```powershell
.\scripts\run_windows_synthetic_experiments.ps1 -Profile lite -Runs 10000 -Warmups 0 -Output results_lite_10k_small -Degree 3 -BaseNodes 200 -ScalabilityNodes "100,300,500"
```

Proposal-style synthetic run:

```powershell
.\scripts\run_windows_synthetic_experiments.ps1 -Profile proposal -Runs 10000 -Warmups 200 -Output results_proposal
```

The proposal profile runs synthetic experiments 1, 2, 3, 4, 5, and 7. Experiment 6 is real Thai routes, so it is intentionally excluded from the synthetic-data sweep.

## Bash Setup With uv

On Linux, macOS, or Git Bash/WSL:

```bash
chmod +x scripts/run_bash_synthetic_experiments.sh scripts/run_synthetic_100.sh
./scripts/run_synthetic_100.sh
```

The 100-run config lives at:

```text
configs/synthetic_100.env
```

It runs all synthetic experiments 1, 2, 3, 4, 5, and 7 with `100` timed runs each:

```text
PROFILE=lite
RUNS=100
WARMUPS=0
OUTPUT=results_synthetic_100
DEGREE=3
BASE_NODES=300
SCALABILITY_NODES=100,300,1000
```

You can also run the flexible bash script with inline overrides:

```bash
PROFILE=lite RUNS=100 WARMUPS=0 OUTPUT=results_synthetic_100 DEGREE=3 BASE_NODES=300 SCALABILITY_NODES=100,300,1000 ./scripts/run_bash_synthetic_experiments.sh
```

## Project Layout

```text
src/ada_route_opt/
  algorithms.py      Core Dijkstra, Greedy, DP, A*, RF-A*, PF-A*
  graph.py           Graph and result data structures
  synthetic.py       Synthetic benchmark graph generator
  metrics.py         Timing and result helpers
scripts/
  run_synthetic_experiment.py
  run_all_experiments.py
tests/
  test_algorithms.py
```

## Notes

- Fuel is discretized by `fuel_step_liters`, default `1.0 L`, matching the proposal's `F = C / epsilon`.
- Travel has zero monetary edge cost. Monetary cost is paid only on refuel actions.
- `PF-A*` includes the fuel-level-aware heuristic described in the proposal. The benchmark cross-checks its returned cost against Dijkstra.
- Real OSM/EPPO ingestion is intentionally left as an integration layer because the exact source format can change. The core algorithms accept any graph loaded into `FuelGraph`.
