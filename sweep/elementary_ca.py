"""Elementary (1D, 2-state, radius-1) cellular automaton sweep.

Sweeps all 256 Wolfram rules, scores each for a rough notion of
"interesting" (not dead, not trivially periodic, not pure noise), and
returns the top N for rendering.
"""
from __future__ import annotations

import numpy as np


def step(row: np.ndarray, rule_bits: np.ndarray) -> np.ndarray:
    left = np.roll(row, 1)
    right = np.roll(row, -1)
    idx = (left << 2) | (row << 1) | right
    return rule_bits[idx]


def simulate(
    rule: int, width: int = 201, height: int = 200, seed: int | None = None
) -> np.ndarray:
    """seed=None: classic single-cell start (the standard way to
    characterize a rule's fundamental behavior class). seed=<int>: random
    binary initial row instead - a legitimate, different way to probe the
    same rule, and the mechanism the daily sweep uses to avoid finding the
    exact same "top 6" every single day."""
    rule_bits = np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)
    grid = np.zeros((height, width), dtype=np.uint8)
    if seed is None:
        grid[0, width // 2] = 1
    else:
        rng = np.random.default_rng(seed)
        grid[0] = (rng.random(width) < 0.5).astype(np.uint8)
    for r in range(1, height):
        grid[r] = step(grid[r - 1], rule_bits)
    return grid


def score(grid: np.ndarray) -> float:
    """Rough complexity heuristic: reward variation row-to-row and column
    density that's neither near-zero nor near-total, penalize exact
    periodicity (a cycle that repeats with a short period)."""
    density = grid.mean()
    if density < 0.02 or density > 0.85:
        return 0.0

    row_diffs = np.abs(np.diff(grid.astype(np.int8), axis=0)).mean()

    # Penalize short-period repetition in the last third of the run.
    tail = grid[-60:]
    period_penalty = 0.0
    for period in (1, 2, 3, 4):
        if len(tail) > period * 2:
            a, b = tail[:-period], tail[period:]
            if np.array_equal(a[-20:], b[-20:]):
                period_penalty = 1.0
                break

    return float(row_diffs * (1.0 - period_penalty))


def sweep(top_n: int = 6, seed: int | None = None) -> list[dict]:
    results = []
    for rule in range(256):
        grid = simulate(rule, seed=seed)
        s = score(grid)
        results.append({"rule": rule, "score": s, "grid": grid})
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]
