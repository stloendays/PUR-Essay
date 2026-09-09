from __future__ import annotations

import math

from pur_bridge.temperature import AndradeFit, fit_andrade  # frozen, reused unchanged

R_GAS_KJ_PER_MOL_K = 8.314462618e-3


def two_point_activation_energy_kj_mol(eta_low: float, eta_high: float, t_low_c: float = 80.0, t_high_c: float = 120.0) -> float:
    """Apparent flow activation energy from two temperatures under ln(eta) = A + B/T, Ea = R B.

    This is the descriptor stored for candidates (e.g. 61.43 kJ/mol for the ORACLE V2 optimum).
    It is a two-point Andrade slope, not a fitted multi-point Ea.
    """
    if eta_low <= 0 or eta_high <= 0:
        raise ValueError("viscosities must be positive")
    t_low = t_low_c + 273.15
    t_high = t_high_c + 273.15
    if t_low == t_high:
        raise ValueError("temperatures must differ")
    b = math.log(eta_low / eta_high) / (1.0 / t_low - 1.0 / t_high)
    return R_GAS_KJ_PER_MOL_K * b


__all__ = ["AndradeFit", "fit_andrade", "two_point_activation_energy_kj_mol", "R_GAS_KJ_PER_MOL_K"]
