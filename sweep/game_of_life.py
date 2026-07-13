"""Conway's Game of Life, for a visually richer render than the 1D sweep."""
from __future__ import annotations

import numpy as np


def step(grid: np.ndarray) -> np.ndarray:
    neighbors = sum(
        np.roll(np.roll(grid, dy, axis=0), dx, axis=1)
        for dy in (-1, 0, 1)
        for dx in (-1, 0, 1)
        if (dy, dx) != (0, 0)
    )
    return ((neighbors == 3) | (grid & (neighbors == 2))).astype(np.uint8)


def random_soup(size: int = 80, density: float = 0.25, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return (rng.random((size, size)) < density).astype(np.uint8)


def simulate(seed: int = 0, size: int = 80, frames: int = 150) -> list[np.ndarray]:
    grid = random_soup(size=size, seed=seed)
    out = [grid.copy()]
    for _ in range(frames - 1):
        grid = step(grid)
        out.append(grid.copy())
    return out
