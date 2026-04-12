from __future__ import annotations

import time
from collections.abc import Callable

from .graph import RouteResult


def timed_run(fn: Callable[..., RouteResult], *args, **kwargs) -> RouteResult:
    start = time.perf_counter_ns()
    result = fn(*args, **kwargs)
    end = time.perf_counter_ns()
    result.runtime_ms = (end - start) / 1_000_000
    return result


def result_row(result: RouteResult) -> dict[str, object]:
    return {
        "algorithm": result.algorithm,
        "feasible": result.feasible,
        "cost": result.cost,
        "runtime_ms": result.runtime_ms,
        "expanded_states": result.expanded_states,
        "path": "->".join(result.path),
        "actions": " | ".join(result.actions),
    }

