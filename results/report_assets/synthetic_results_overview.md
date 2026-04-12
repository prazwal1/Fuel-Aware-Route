# Synthetic Experiment Results Overview

## Experiment 1: Scalability
- Fastest feasible algorithm overall: PF-A* with mean runtime 60.06 ms.
- Lowest mean cost overall: State-Expanded Dijkstra with mean cost 2876.88.
- Highest feasibility rate: State-Expanded Dijkstra at 100.0%.
- Algorithms with incomplete feasibility in this experiment: Greedy Refuel.
- Generated charts:
  - `results/report_assets/exp1_scalability/exp1_scalability_runtime.png`
  - `results/report_assets/exp1_scalability/exp1_scalability_expanded_states.png`
  - `results/report_assets/exp1_scalability/exp1_scalability_cost.png`
  - `results/report_assets/exp1_scalability/exp1_scalability_feasibility.png`

## Experiment 2: Price Variance
- Fastest feasible algorithm overall: RF-A* with mean runtime 17.90 ms.
- Lowest mean cost overall: State-Expanded Dijkstra with mean cost 2576.21.
- Highest feasibility rate: State-Expanded Dijkstra at 100.0%.
- Algorithms with incomplete feasibility in this experiment: Greedy Refuel.
- Generated charts:
  - `results/report_assets/exp2_price_variance/exp2_price_variance_runtime.png`
  - `results/report_assets/exp2_price_variance/exp2_price_variance_expanded_states.png`
  - `results/report_assets/exp2_price_variance/exp2_price_variance_cost.png`
  - `results/report_assets/exp2_price_variance/exp2_price_variance_feasibility.png`

## Experiment 3: Tank Capacity
- Fastest feasible algorithm overall: PF-A* with mean runtime 18.94 ms.
- Lowest mean cost overall: State-Expanded Dijkstra with mean cost 2185.84.
- Highest feasibility rate: State-Expanded Dijkstra at 100.0%.
- Algorithms with incomplete feasibility in this experiment: Greedy Refuel.
- Generated charts:
  - `results/report_assets/exp3_tank_capacity/exp3_tank_capacity_runtime.png`
  - `results/report_assets/exp3_tank_capacity/exp3_tank_capacity_expanded_states.png`
  - `results/report_assets/exp3_tank_capacity/exp3_tank_capacity_cost.png`
  - `results/report_assets/exp3_tank_capacity/exp3_tank_capacity_feasibility.png`

## Experiment 4: Initial Fuel
- Fastest feasible algorithm overall: PF-A* with mean runtime 46.98 ms.
- Lowest mean cost overall: State-Expanded Dijkstra with mean cost 2831.54.
- Highest feasibility rate: State-Expanded Dijkstra at 100.0%.
- Algorithms with incomplete feasibility in this experiment: Greedy Refuel.
- Generated charts:
  - `results/report_assets/exp4_initial_fuel/exp4_initial_fuel_runtime.png`
  - `results/report_assets/exp4_initial_fuel/exp4_initial_fuel_expanded_states.png`
  - `results/report_assets/exp4_initial_fuel/exp4_initial_fuel_cost.png`
  - `results/report_assets/exp4_initial_fuel/exp4_initial_fuel_feasibility.png`

## Experiment 5: RF-A* vs PF-A*
- Fastest feasible algorithm overall: PF-A* with mean runtime 58.62 ms.
- Lowest mean cost overall: PF-A* with mean cost 1967.01.
- Highest feasibility rate: RF-A* at 100.0%.
- Algorithms with incomplete feasibility in this experiment: PF-A*, RF-A*.
- At sigma pct=5.0, PF-A* is the fastest feasible method at 60.66 ms.
- At sigma pct=10.0, PF-A* is the fastest feasible method at 59.92 ms.
- At sigma pct=20.0, PF-A* is the fastest feasible method at 58.62 ms.
- Generated charts:
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_runtime_sigma_pct_5_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_runtime_sigma_pct_10_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_runtime_sigma_pct_20_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_expanded_states_sigma_pct_5_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_expanded_states_sigma_pct_10_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_expanded_states_sigma_pct_20_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_cost_sigma_pct_5_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_cost_sigma_pct_10_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_cost_sigma_pct_20_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_feasibility_sigma_pct_5_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_feasibility_sigma_pct_10_0.png`
  - `results/report_assets/exp5_rf_vs_pf/exp5_rf_vs_pf_feasibility_sigma_pct_20_0.png`

## Experiment 7: Variable Fill vs Full Tank
- Fastest feasible algorithm overall: Full-Tank-Only Dijkstra with mean runtime 10.04 ms.
- Lowest mean cost overall: State-Expanded Dijkstra with mean cost 1614.40.
- Highest feasibility rate: State-Expanded Dijkstra at 100.0%.
- At sigma pct=0.0, Full-Tank-Only Dijkstra is the fastest feasible method at 10.04 ms.
- At sigma pct=5.0, Full-Tank-Only Dijkstra is the fastest feasible method at 10.35 ms.
- At sigma pct=10.0, Full-Tank-Only Dijkstra is the fastest feasible method at 10.26 ms.
- At sigma pct=20.0, Full-Tank-Only Dijkstra is the fastest feasible method at 10.57 ms.
- Generated charts:
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_runtime_sigma_pct_0_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_runtime_sigma_pct_5_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_runtime_sigma_pct_10_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_runtime_sigma_pct_20_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_expanded_states_sigma_pct_0_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_expanded_states_sigma_pct_5_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_expanded_states_sigma_pct_10_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_expanded_states_sigma_pct_20_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_cost_sigma_pct_0_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_cost_sigma_pct_5_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_cost_sigma_pct_10_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_cost_sigma_pct_20_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_feasibility_sigma_pct_0_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_feasibility_sigma_pct_5_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_feasibility_sigma_pct_10_0.png`
  - `results/report_assets/exp7_variable_vs_full_tank/exp7_variable_vs_full_tank_feasibility_sigma_pct_20_0.png`
