# Experiment 6 Real-Route Study

## Dataset Shape

The current real-route dataset contains three curated Thai corridor instances:

- `bkk_to_cnx` for Bangkok to Chiang Mai
- `bkk_to_hkt` for Bangkok to Phuket
- `bkk_to_kkc` for Bangkok to Khon Kaen

All three use:

- `40.0 L` tank capacity
- `28.0 L` initial fuel
- `10.0 km/L` efficiency
- `2026-04-03` Gasohol 91 price snapshot

The generated instances are corridor abstractions with synthetic intermediate station nodes and province-based prices, not raw OSM station graphs.

## Instance Summary

| Instance | Route | Stations | Directed Edges | Notes |
| --- | --- | ---: | ---: | --- |
| `bkk_to_cnx` | Bangkok to Chiang Mai | 27 | 522 | Northern long-haul corridor |
| `bkk_to_hkt` | Bangkok to Phuket | 31 | 624 | Longest corridor in the dataset |
| `bkk_to_kkc` | Bangkok to Khon Kaen | 18 | 286 | Shorter northeastern corridor |

## One-Pass Algorithm Study

| Corridor | Algorithm | Feasible | Cost (THB) | Expanded States | Path Length |
| --- | --- | --- | ---: | ---: | ---: |
| Bangkok to Chiang Mai | Dijkstra | Yes | 2106.04 | 802 | 5 |
| Bangkok to Chiang Mai | Dynamic Programming | Yes | 2106.04 | 802 | 5 |
| Bangkok to Chiang Mai | Full-Tank-Only Dijkstra | Yes | 2238.58 | 721 | 6 |
| Bangkok to Chiang Mai | Greedy | No | inf | 4320 | 0 |
| Bangkok to Chiang Mai | Standard A* | Yes | 2106.04 | 1360 | 5 |
| Bangkok to Chiang Mai | RF-A* | Yes | 2106.04 | 1360 | 5 |
| Bangkok to Chiang Mai | PF-A* | Yes | 2106.04 | 802 | 5 |
| Bangkok to Phuket | Dijkstra | Yes | 2734.66 | 975 | 6 |
| Bangkok to Phuket | Dynamic Programming | Yes | 2734.66 | 975 | 6 |
| Bangkok to Phuket | Full-Tank-Only Dijkstra | Yes | 2779.24 | 865 | 6 |
| Bangkok to Phuket | Greedy | No | inf | 4960 | 0 |
| Bangkok to Phuket | Standard A* | Yes | 2736.16 | 1610 | 5 |
| Bangkok to Phuket | RF-A* | Yes | 2736.16 | 1610 | 5 |
| Bangkok to Phuket | PF-A* | Yes | 2734.66 | 975 | 6 |
| Bangkok to Khon Kaen | Dijkstra | Yes | 1004.44 | 441 | 4 |
| Bangkok to Khon Kaen | Dynamic Programming | Yes | 1004.44 | 441 | 4 |
| Bangkok to Khon Kaen | Full-Tank-Only Dijkstra | Yes | 1048.32 | 400 | 4 |
| Bangkok to Khon Kaen | Greedy | No | inf | 2880 | 0 |
| Bangkok to Khon Kaen | Standard A* | Yes | 1006.04 | 749 | 4 |
| Bangkok to Khon Kaen | RF-A* | Yes | 1006.04 | 749 | 4 |
| Bangkok to Khon Kaen | PF-A* | Yes | 1004.44 | 441 | 4 |

## Corridor-Level Findings

- PF-A* matches Dijkstra and Dynamic Programming on all three corridor instances.
- Full-tank-only is more expensive than the variable-purchase optimum on all three corridors.
- Savings over full-tank-only are `132.54 THB (5.92%)` for Chiang Mai, `44.58 THB (1.60%)` for Phuket, and `43.88 THB (4.19%)` for Khon Kaen.
- PF-A* expands fewer states than RF-A* on all three corridors.
- Standard A* and RF-A* still show small positive cost gaps on Phuket and Khon Kaen.
- Greedy is infeasible on all three current corridor graphs.

## Recommended Experiment 6 Framing

Experiment 6 should be written as a **three-corridor real-route case study** validating:

1. the practical savings of variable purchase over full-tank-only routing on curated Thai intercity corridors,
2. the state-expansion advantage of PF-A* over RF-A* on those corridors, and
3. the current correctness status of the heuristic solvers on real-route data.
