# Demo Commands

These demos are safe to run live because they use the existing package code and checked-in data only.

Run from the repository root:

```bash
bash demo/running_example_demo.sh
bash demo/real_corridor_demo.sh
```

## Demo 1: Running Example

Shows all six algorithms on the small worked example:

- State-Expanded Dijkstra
- Greedy Refuel
- Dynamic Programming
- Standard A*
- RF-A*
- PF-A*

Expected point to explain: Dijkstra, DP, and PF-A* return the optimal cost of `216.0` THB, while Greedy is feasible but more expensive.

## Demo 2: Real Thai Corridors

Shows the real-route comparison between variable-purchase routing, PF-A*, and full-tank-only routing.

Expected point to explain: variable-purchase routing saves fuel cost on all three real corridors.
