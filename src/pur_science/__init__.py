"""Deterministic, non-Agent science layer for PUR-Essay.

Everything in this package is pure arithmetic on frozen inputs. It owns the
objective, feasibility gates, decision frontier (L0/L1/L2), backward
threshold solving, reachability and local trend directions. The Agent layer
(`pur_agent`) calls into this package through tools; it never re-implements
any scoring rule.
"""

from .canonical import CanonicalTable, canonicalize, parse_blend
from .objective import window_center, property_score, mdi_fraction
from .frontier import compute_frontier, frontier_decision
from .backward import solve_backward_threshold
from .reachability import check_reachability
from .rheology import two_point_activation_energy_kj_mol, fit_andrade

__all__ = [
    "CanonicalTable", "canonicalize", "parse_blend",
    "window_center", "property_score", "mdi_fraction",
    "compute_frontier", "frontier_decision",
    "solve_backward_threshold", "check_reachability",
    "two_point_activation_energy_kj_mol", "fit_andrade",
]
