from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .backward import BackwardSolution, local_manifold
from .canonical import CID, MDI_FRACTION, NCO, CanonicalTable


@dataclass(frozen=True)
class Reachability:
    blend: str
    continuous_threshold: float | None
    grid_values: tuple[float, ...]
    nearest_reachable_grid_value: float | None
    nearest_reachable_candidate_id: str | None
    reachable: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_reachability(table: CanonicalTable, solution: BackwardSolution, *, grid_tol: float = 1e-9) -> Reachability:
    """Project the continuous backward threshold onto the discrete NCO:OH grid of the same blend.

    The first grid point at or above the continuous threshold whose MDI fraction actually
    satisfies the bound is the reachable formulation. Reachability is False when no grid
    point of that blend satisfies the constraint.
    """
    local = local_manifold(table, solution.blend)
    grid = tuple(float(x) for x in local[NCO].to_numpy(dtype=float))
    ok = local[local[MDI_FRACTION].ge(solution.threshold - grid_tol)]
    if solution.continuous_threshold is not None:
        ok = ok[ok[NCO].ge(solution.continuous_threshold - grid_tol)]
    if ok.empty:
        return Reachability(solution.blend, solution.continuous_threshold, grid, None, None, False,
                            "no grid point of this blend satisfies the constraint")
    first = ok.sort_values(NCO).iloc[0]
    return Reachability(
        blend=solution.blend,
        continuous_threshold=solution.continuous_threshold,
        grid_values=grid,
        nearest_reachable_grid_value=float(first[NCO]),
        nearest_reachable_candidate_id=str(first[CID]),
        reachable=True,
        reason="first discrete NCO:OH grid point at or above the continuous threshold",
    )
