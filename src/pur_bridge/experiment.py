from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import math
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

from .anchors import AnchorMechanismModel
from .temperature import fit_andrade

REQUIRED_COLUMNS = {"batch_id", "stage", "temp_c", "replicate_id", "viscosity_pa_s"}

@dataclass(frozen=True)
class PrimaryEndpoint:
    n_batches: int
    geometric_mean_pa_s: float
    log_sd_between_batches: float | None
    ci95_low_pa_s: float | None
    ci95_high_pa_s: float | None
    classification: str
    theta: float


def load_e6_measurements(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing measurement columns: {sorted(missing)}")
    if (df["viscosity_pa_s"] <= 0).any():
        raise ValueError("All viscosity measurements must be positive")
    allowed_stages = {"blend", "prepolymer"}
    bad = set(df["stage"].astype(str)).difference(allowed_stages)
    if bad:
        raise ValueError(f"Unknown stages: {sorted(bad)}")
    return df


def batch_means(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby(["batch_id", "stage", "temp_c"], as_index=False)
        .agg(
            viscosity_mean_pa_s=("viscosity_pa_s", "mean"),
            viscosity_sd_pa_s=("viscosity_pa_s", "std"),
            n_technical=("viscosity_pa_s", "size"),
        )
    )
    out["technical_cv_pct"] = 100.0 * out["viscosity_sd_pa_s"] / out["viscosity_mean_pa_s"]
    return out


def summarize_primary_endpoint(df: pd.DataFrame, model: AnchorMechanismModel) -> PrimaryEndpoint:
    bm = batch_means(df)
    primary = bm[(bm["stage"] == "prepolymer") & (bm["temp_c"] == 130)]
    vals = primary["viscosity_mean_pa_s"].to_numpy(dtype=float)
    if len(vals) == 0:
        raise ValueError("No prepolymer 130 C measurements found")
    logs = np.log(vals)
    gmean = float(np.exp(np.mean(logs)))
    if len(vals) >= 2:
        log_sd = float(np.std(logs, ddof=1))
        se = log_sd / math.sqrt(len(vals))
        crit = float(student_t.ppf(0.975, df=len(vals)-1))
        lo = float(np.exp(np.mean(logs) - crit * se))
        hi = float(np.exp(np.mean(logs) + crit * se))
    else:
        log_sd, lo, hi = None, None, None
    return PrimaryEndpoint(
        n_batches=int(len(vals)),
        geometric_mean_pa_s=gmean,
        log_sd_between_batches=log_sd,
        ci95_low_pa_s=lo,
        ci95_high_pa_s=hi,
        classification=model.classify(gmean),
        theta=model.context_transfer_theta(gmean),
    )


def andrade_by_batch(df: pd.DataFrame) -> pd.DataFrame:
    bm = batch_means(df)
    rows = []
    for (batch_id, stage), g in bm.groupby(["batch_id", "stage"]):
        g = g.sort_values("temp_c")
        if g["temp_c"].nunique() < 3:
            continue
        fit = fit_andrade(g["temp_c"].to_numpy(), g["viscosity_mean_pa_s"].to_numpy())
        rows.append({
            "batch_id": batch_id,
            "stage": stage,
            "andrade_intercept": fit.intercept,
            "andrade_slope_k": fit.slope_k,
            "andrade_r2": fit.r2,
            "n_points": fit.n_points,
        })
    return pd.DataFrame(rows)


def endpoint_to_dict(endpoint: PrimaryEndpoint) -> dict:
    return asdict(endpoint)
