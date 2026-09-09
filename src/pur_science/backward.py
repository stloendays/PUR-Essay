from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd

from .canonical import BLEND, CID, MDI_FRACTION, MDI_PARTS, NCO, CanonicalTable


@dataclass(frozen=True)
class BackwardSolution:
    constraint: str
    variable: str
    blend: str
    threshold: float
    candidate_value: float
    continuous_threshold: float | None
    manifold_slope_mdi_parts_per_nco: float | None
    manifold_is_linear: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def local_manifold(table: CanonicalTable, blend: str) -> pd.DataFrame:
    local = table.frame[table.frame[BLEND] == blend].sort_values(NCO)
    if local.empty:
        raise KeyError(f"No candidates with blend {blend!r}")
    return local


def solve_backward_threshold(
    table: CanonicalTable,
    candidate_id: str,
    *,
    threshold: float,
    constraint: str = "mdi_fraction_min",
    rel_tol: float = 1e-6,
) -> BackwardSolution:
    """Minimum NCO:OH at which the candidate's blend reaches the MDI-fraction lower bound.

    On the frozen design manifold, mdi_parts = k * nco_oh for a fixed blend (k is the blend's
    MDI demand per unit NCO:OH). Then mdi_fraction = k n / (B + k n) and the continuous
    threshold is n* = f (B) / (k (1 - f)). If the local table is not exactly linear, the
    threshold is obtained by monotone interpolation on the observed grid instead.
    """
    if constraint != "mdi_fraction_min":
        raise ValueError("Only the mdi_fraction_min backward problem is frozen in FRONTIER V1")
    row = table.row(candidate_id)
    blend = str(row[BLEND])
    local = local_manifold(table, blend)
    n = local[NCO].to_numpy(dtype=float)
    m = local[MDI_PARTS].to_numpy(dtype=float)
    f = local[MDI_FRACTION].to_numpy(dtype=float)
    k = m / n
    linear = bool(np.allclose(k, k[0], rtol=rel_tol, atol=0.0))
    basis = table.polyol_basis_parts
    if linear:
        slope = float(k[0])
        continuous = float(threshold * basis / (slope * (1.0 - threshold)))
        reason = "exact solution on the linear MDI-demand manifold mdi_parts = k * nco_oh"
    else:
        slope = None
        order = np.argsort(f)
        if not (f.min() <= threshold <= f.max()):
            continuous = None
            reason = "threshold lies outside the observed local manifold and the manifold is not linear"
        else:
            continuous = float(np.interp(threshold, f[order], n[order]))
            reason = "monotone interpolation on the observed local grid (manifold not exactly linear)"
    return BackwardSolution(
        constraint=constraint,
        variable="nco_oh",
        blend=blend,
        threshold=float(threshold),
        candidate_value=float(row[MDI_FRACTION]),
        continuous_threshold=continuous,
        manifold_slope_mdi_parts_per_nco=slope,
        manifold_is_linear=linear,
        reason=reason,
    )
