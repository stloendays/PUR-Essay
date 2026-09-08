import numpy as np
from pur_bridge import fit_andrade


def test_andrade_recovers_synthetic_curve():
    temps = np.array([110.0, 120.0, 130.0])
    a, b = -4.0, 3500.0
    eta = np.exp(a + b / (temps + 273.15))
    fit = fit_andrade(temps, eta)
    assert abs(fit.intercept - a) < 1e-10
    assert abs(fit.slope_k - b) < 1e-8
    assert fit.r2 > 0.999999
