# Experiment 6 Plan

## Goal

Execute Experiment 6 on real Thai corridors in a way that is reproducible, auditable, and strong enough to drop directly into the final report.

## Corridors

- Bangkok to Chiang Mai
- Bangkok to Phuket
- Bangkok to Khon Kaen

## Core Research Questions

- Do the synthetic findings transfer to real Thai road-network instances?
- How much fuel-cost savings does the variable-purchase model achieve over the full-tank-only baseline on real routes?
- Does PF-A* retain its practical runtime and state-expansion advantage on real-route graphs?
- Are Standard A* and RF-A* cost-consistent with the exact baselines after audit and repair?

## Fixed Experimental Parameters

- Tank capacity: `40.0 L`
- Initial fuel: `28.0 L`
- Efficiency: `10.0 km/L`
- Purchase models: `variable`, `full_tank_only`
- Output CSV: `results_real/real_route_results.csv`

## Deliverables

- Clean corridor definitions
- Generated real-route instances in `data/real_routes/generated/*.json`
- Raw collection artifacts in `data/real_routes/raw/`
- Experiment 6 result table in `results_real/real_route_results.csv`
- Report-ready summary tables and figures for the final report
- A short audit note documenting whether Standard A* and RF-A* were repaired before the final run

## Work Breakdown

### Phase 1: Data Preparation

1. Create or finalize a corridor config based on `data/real_routes/corridors.example.json`.
2. Decide the exact endpoint anchoring for each corridor and keep it fixed for the whole experiment.
3. Prepare a station-price file if available, ideally at `data/real_routes/station_prices.csv`.
4. Document the source and date of the price snapshot used for the experiment.

### Phase 2: Real-Route Collection

1. Run:

```powershell
.\scripts\run_windows_collect_real_route_data.ps1 -Config data/real_routes/corridors.example.json -OutputDir data/real_routes/generated -RawDir data/real_routes/raw
```

2. If curated prices are ready, rerun with:

```powershell
.\scripts\run_windows_collect_real_route_data.ps1 -Config data/real_routes/corridors.example.json -OutputDir data/real_routes/generated -RawDir data/real_routes/raw -StationPriceCsv data/real_routes/station_prices.csv
```

3. Confirm the collector writes:

- `data/real_routes/raw/<instance_id>_stations.csv`
- `data/real_routes/generated/<instance_id>.json`

### Phase 3: Instance Validation

Validate every generated JSON before benchmarking.

- Source and destination nodes exist in `stations`
- Distances are in kilometers and are all positive
- Every edge is fuel-feasible under the chosen vehicle settings, or intentionally excluded
- Coordinates are present for stations when possible
- Destination price uses a sentinel only if refueling there is irrelevant
- Each corridor admits at least one feasible path from source to target
- Station-price coverage and fallback assignments are recorded

Recommended checks:

- Count stations and edges per corridor
- Record corridor distance and average station spacing
- Flag unreachable stations or isolated components
- Save a brief validation note per corridor

### Phase 4: Algorithm Audit Before Full Benchmark

This phase is mandatory because the current synthetic results show cost mismatches for Standard A* and RF-A*.

1. Run one correctness pass per corridor with:

- State-Expanded Dijkstra
- Dynamic Programming
- PF-A*
- Standard A*
- RF-A*
- Full-Tank-Only Dijkstra
- Greedy Refuel

2. Compare:

- feasibility
- total cost
- path
- expanded states

3. Require the following before the final benchmark:

- State-Expanded Dijkstra and Dynamic Programming agree on cost
- PF-A* matches the exact baseline cost
- Standard A* and RF-A* either match the exact baseline or are explicitly excluded from final claims
- Any infeasible result is explained by the corridor graph, not by a tooling error

### Phase 5: Benchmark Execution

Run the real-route experiment using the validated instances.

Smoke run:

```powershell
.\scripts\run_windows_real_experiments.ps1 -InstancesDir data/real_routes/generated -Runs 10 -Warmups 0 -Output results_real_smoke -PurchaseModel both
```

Final run:

```powershell
.\scripts\run_windows_real_experiments.ps1 -InstancesDir data/real_routes/generated -Runs 10000 -Warmups 200 -Output results_real -PurchaseModel both
```

Execution notes:

- Keep the machine profile fixed for all final runs
- Record Python version, package versions, CPU, RAM, and OS
- Do not mix results from different corridor definitions or price snapshots
- Archive the exact config used to generate the final CSV

### Phase 6: Result Summarization

For each corridor and purchase model, compute:

- feasibility rate
- mean cost
- runtime mean and standard deviation
- mean expanded states
- chosen path frequency if paths vary across runs

Key comparisons:

- Variable purchase vs full-tank-only cost gap in THB
- Variable purchase vs full-tank-only cost gap in percent
- PF-A* vs RF-A* expanded states
- PF-A* vs exact baselines runtime

### Phase 7: Final Report Integration

Add a dedicated Experiment 6 section to `ADA_Final_Report/chapters/ch8_results_discussion.tex` containing:

- one summary table for all corridors
- one per-corridor cost comparison table
- one figure or map-style visualization per corridor
- a short discussion connecting real-route findings to Experiments 1, 5, and 7
- an explicit note on algorithm correctness status after the audit

## Suggested Table Structure

### Table A: Corridor Overview

- corridor
- source
- target
- route distance
- number of stations
- number of edges
- purchase model

### Table B: Algorithm Performance

- corridor
- algorithm
- feasible
- mean cost
- runtime ms
- expanded states

### Table C: Practical Savings

- corridor
- variable-purchase cost
- full-tank-only cost
- savings THB
- savings percent

## Risks and Mitigations

- OSM extraction may include noisy or duplicate stations.
  Mitigation: deduplicate by OSM id and inspect station spacing manually.

- Provincial price mapping may be incomplete.
  Mitigation: document fallback rules and quantify how many stations used fallback prices.

- Some corridor transitions may be longer than the vehicle range.
  Mitigation: validate fuel-feasibility during graph construction and reject invalid edges early.

- Standard A* and RF-A* may remain inconsistent with exact baselines.
  Mitigation: complete the algorithm audit before the final 10,000-run benchmark and exclude broken variants from strong optimality claims if unresolved.

- Final runs may be slow.
  Mitigation: run a smoke pass first, estimate wall-clock time, then schedule the strict run on a stable machine.

## Definition of Done

Experiment 6 is complete when all of the following are true:

- Three corridor JSON instances are generated and validated
- Price-assignment rules are frozen and documented
- A correctness pass has been completed and recorded
- `results_real/real_route_results.csv` has been produced from the final run
- Final report tables and figures for Experiment 6 are created
- `ADA_Final_Report` has been updated with the real-route findings and final conclusions
