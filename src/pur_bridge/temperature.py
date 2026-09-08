from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class AndradeFit:
    intercept: float
    slope_k: float
    r2: float
    n_points: int

    def predict_eta(self, temp_c: float) -> float:
        temp_k = temp_c + 273.15
        return float(np.exp(self.intercept + self.slope_k / temp_k))


def fit_andrade(temp_c, eta_pa_s) -> AndradeFit:
    t = np.asarray(temp_c, dtype=float)
    eta = np.asarray(eta_pa_s, dtype=float)
    if t.ndim != 1 or eta.ndim != 1 or len(t) != len(eta):
        raise ValueError("temp_c and eta_pa_s must be one-dimensional arrays of equal length")
    if len(t) < 3:
        raise ValueError("At least three temperature points are required for the preregistered fit")
    if np.any(eta <= 0):
        raise ValueError("viscosity values must be positive")
    x = 1.0 / (t + 273.15)
    y = np.log(eta)
    slope, intercept = np.polyfit(x, y, 1)
    pred = intercept + slope * x
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 if ss_tot == 0 else 1.0 - ss_res / ss_tot
    return AndradeFit(float(intercept), float(slope), float(r2), int(len(t)))
