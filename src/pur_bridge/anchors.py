from __future__ import annotations
import math
from dataclasses import dataclass
from pathlib import Path
import pandas as pd

@dataclass(frozen=True)
class HypothesisPrediction:
    name: str
    eta_pa_s: float
    log_eta: float
    transfer_log_effect: float

class AnchorMechanismModel:
    """Local, auditable model for the missing C-rich/high-A patent cell."""
    def __init__(self, anchor_csv: str | Path):
        self.df = pd.read_csv(anchor_csv).set_index("id")
        required = {"E1", "E2", "E3", "E4", "E5"}
        missing = required.difference(self.df.index)
        if missing:
            raise ValueError(f"Missing frozen anchors: {sorted(missing)}")

    def eta(self, key: str) -> float:
        return float(self.df.loc[key, "eta130_pa_s"])

    @property
    def delta_balanced(self) -> float:
        return math.log(self.eta("E2") / self.eta("E1"))

    @property
    def delta_D_rich(self) -> float:
        return math.log(self.eta("E4") / self.eta("E3"))

    def predictions(self) -> dict[str, HypothesisPrediction]:
        base = self.eta("E5")
        vals = {"H_strong": self.delta_balanced, "H_weak": self.delta_D_rich}
        return {
            name: HypothesisPrediction(
                name=name,
                eta_pa_s=base * math.exp(delta),
                log_eta=math.log(base) + delta,
                transfer_log_effect=delta,
            )
            for name, delta in vals.items()
        }

    def equal_prior_boundary_pa_s(self) -> float:
        p = self.predictions()
        return math.sqrt(p["H_strong"].eta_pa_s * p["H_weak"].eta_pa_s)

    def context_transfer_theta(self, eta_e6_pa_s: float) -> float:
        if eta_e6_pa_s <= 0:
            raise ValueError("eta_e6_pa_s must be positive")
        observed_delta = math.log(eta_e6_pa_s / self.eta("E5"))
        denom = self.delta_balanced - self.delta_D_rich
        return (observed_delta - self.delta_D_rich) / denom

    def log_bayes_factor_strong_vs_weak(self, eta_e6_pa_s: float, sigma_log: float) -> float:
        if eta_e6_pa_s <= 0 or sigma_log <= 0:
            raise ValueError("positive eta and sigma required")
        y = math.log(eta_e6_pa_s)
        p = self.predictions()
        ms = p["H_strong"].log_eta
        mw = p["H_weak"].log_eta
        return -0.5 * (((y-ms)/sigma_log)**2 - ((y-mw)/sigma_log)**2)

    def classify(self, eta_e6_pa_s: float, weak_max: float = 33.0, strong_min: float = 40.0) -> str:
        if eta_e6_pa_s <= weak_max:
            return "weak_consistent"
        if eta_e6_pa_s >= strong_min:
            return "strong_consistent"
        return "indeterminate"
