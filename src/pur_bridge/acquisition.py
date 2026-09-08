from __future__ import annotations
import math
import numpy as np


def _normal_pdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    z = (x-mu)/sigma
    return np.exp(-0.5*z*z)/(sigma*math.sqrt(2*math.pi))


def binary_gaussian_information_gain(mu_a: float, mu_b: float, sigma: float, grid_n: int = 20001) -> float:
    """Mutual information I(H;Y) in nats for two equal-prior Gaussians."""
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    lo = min(mu_a, mu_b) - 8*sigma
    hi = max(mu_a, mu_b) + 8*sigma
    x = np.linspace(lo, hi, grid_n)
    pa = _normal_pdf(x, mu_a, sigma)
    pb = _normal_pdf(x, mu_b, sigma)
    mix = 0.5*(pa+pb)
    eps = np.finfo(float).tiny
    integrand = 0.5*pa*np.log((pa+eps)/(mix+eps)) + 0.5*pb*np.log((pb+eps)/(mix+eps))
    return float(np.trapezoid(integrand, x))
