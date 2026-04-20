# Experiment 6 Real-Route Overview

- Total result rows: 210000
- Timed runs per corridor/algorithm combination: 10,000
- Corridors covered: Bangkok to Chiang Mai, Bangkok to Phuket, Bangkok to Khon Kaen

## Key Findings
- PF-A* matches State-Expanded Dijkstra on all three real-route corridors.
- Full-tank-only Dijkstra is more expensive than the variable-purchase optimum on every corridor.
- Standard A* and RF-A* still show small positive cost gaps on Phuket and Khon Kaen.
- Greedy is infeasible on all three current corridor graphs.

## Savings Summary
- Bangkok to Chiang Mai: 132.54 THB saved (5.92%).
- Bangkok to Phuket: 44.58 THB saved (1.60%).
- Bangkok to Khon Kaen: 43.88 THB saved (4.19%).
