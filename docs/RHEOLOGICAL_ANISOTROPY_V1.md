# Rheological anisotropy analysis V1

**Status:** working scientific analysis for manuscript v0.4. This note refines the chemistry/rheology claim without changing any measured value or the frozen PUR-FRONTIER/PUR-RECOVER benchmarks.

## 1. Question

The useful question is not whether temperature and time can both affect polyurethane rheology; that is established prior art. The manuscript-relevant question is whether, **within the local reactive-PUR formulation space studied here**, formulation/process perturbations act symmetrically on all rheological coordinates or whether most variability is concentrated in some coordinates while others remain comparatively constrained.

Working formulation:

> **Reactive PUR exhibits anisotropic rheological variability: absolute viscosity level and temporal drift change strongly across realizations/formulations, whereas the local temperature-response slope is comparatively conserved.**

This is a local empirical statement, not a universal claim that polyurethane flow activation energy is composition-independent.

## 2. Experimental data used

Source: `data/prospective_validation/experimental_viscosity_v1.csv`.

Temperature sweeps:
- 7 experimental realizations;
- 6 temperatures per realization (80, 90, 100, 110, 120, 130 C);
- 42 viscosity observations total;
- realizations: E1 initial, E1 day-1 repeat, E2 GJJ, E2 ZYX, E2 CHH, E2 ZYX day-1 repeat, E3 CHH.

Thermal-hold data at 120 C:
- E1: 15, 30, 60, 90 min;
- E5: 15, 30, 60, 90 min;
- corrected formulation: two repeat runs at 15, 30, 45, 60 min.

## 3. Temperature-response structure

For each temperature-sweep realization, fit

```text
ln(eta) = a + Ea/(R*T).
```

Across the seven realizations:

```text
mean apparent Ea = 41.868 kJ mol^-1
SD               = 2.267 kJ mol^-1
CV               = 5.415%
individual R^2   = 0.9651-0.9979
```

The raw six-temperature viscosity vectors also occupy an unusually narrow direction in response space:

```text
PC1 variance explained = 99.630%
pairwise cosine similarity:
  mean = 0.999079
  min  = 0.997333
  max  = 0.999950
```

This does **not** mean the absolute viscosity values are similar. It means that the temperature-response vectors are nearly collinear despite large level shifts.

### 3.1 Does formulation require a different temperature slope?

Restricted model:

```text
ln(eta) ~ 1/T + formulation
```

Full model:

```text
ln(eta) ~ (1/T) * formulation
```

Adding formulation-specific temperature slopes does not improve fit:

```text
F = 0.0159
p = 0.98425
df difference = 2
```

### 3.2 Does each experimental realization require a different temperature slope?

Restricted model:

```text
ln(eta) ~ 1/T + realization
```

Full model:

```text
ln(eta) ~ (1/T) * realization
```

Adding realization-specific slopes is also unsupported in the current dataset:

```text
F = 1.2417
p = 0.31554
df difference = 6
```

Paper-facing interpretation:

> Within this local design space, the available data do not require formulation- or realization-specific temperature slopes to describe the 80-130 C response.

The safe claim is **comparative local conservation**, not exact invariance and not universality across PUR chemistry.

## 4. Absolute viscosity is strongly realization-dependent

The same nominal E2 formulation spans:

```text
80 C:  max/min = 2.89x
120 C: max/min = 3.57x
```

across the GJJ/ZYX/CHH realizations.

A composition-only model,

```text
ln(eta) ~ 1/T + formulation
```

gives

```text
R^2  = 0.89516
RMSE = 0.33199 in ln(eta)
```

Replacing nominal formulation identity with realization identity,

```text
ln(eta) ~ 1/T + realization
```

gives

```text
R^2  = 0.99585
RMSE = 0.06605 in ln(eta)
RMSE reduction = 80.1%
```

The nested-model comparison is large:

```text
F = 206.26
p = 2.49e-23
df difference = 4
```

A leave-one-temperature-out interpolation test gives:

```text
composition/formulation-only RMSE = 0.34084
realization-aware RMSE            = 0.10479
error reduction                   = 69.3%
```

This is **temperature interpolation for already observed realizations**, not external prediction of a completely unseen batch.

A mixed-effects model with formulation and 1/T as fixed effects and realization as a random intercept gives, using maximum-likelihood estimation:

```text
realization variance = 0.10498
residual variance    = 0.00523
conditional ICC      = 0.9525
```

Interpretation:

> after accounting for temperature and nominal formulation, the remaining structure is dominated by realization-level offsets rather than measurement-scale residual noise.

This should not be reworded as “95% of all viscosity variance comes from process state.”

## 5. Temporal response is strongly formulation-dependent

For E1 and E5, fit the descriptive thermal-hold model

```text
ln(eta(t)) = ln(eta0) + k_drift * t
```

with t in hours:

```text
E1: k_drift = 0.12521 h^-1, R^2 = 0.99937
E5: k_drift = 0.53749 h^-1, R^2 = 0.99724
E5/E1 drift-rate ratio = 4.293
```

Directly observed 120 C drift:

```text
E1, 15->60 min = +9.51%
E1, 15->90 min = +16.85%

E5, 15->60 min = +51.54%
E5, 15->90 min = +93.08%
```

The corrected formulation was measured twice over the common 15-60 min window:

```text
replicate 1 = -0.16%
replicate 2 = +3.04%
mean profile = +1.47%
```

Because the corrected profile is nearly flat, an exponential drift coefficient is not a useful headline descriptor for that formulation; use the directly observed stability index over the matched time window.

## 6. Scientific interpretation

The combined result is better described as **anisotropic rheological variability** than as the simple statement that “temperature and time are different dimensions.”

Observed pattern:

```text
large absolute-level variation
+ large formulation-dependent temporal drift
+ narrow local temperature-slope distribution
= anisotropic response structure
```

A concise manuscript formulation is:

> **Within the investigated reactive-PUR formulation space, composition and experimental realization exert strongly anisotropic control over rheology: absolute viscosity level and temporal evolution change substantially, while the temperature-response slope remains confined to a comparatively narrow range.**

A stronger geometric framing, suitable for Discussion after the statistics are shown, is:

> **The experiments are consistent with a near-common local thermal-response direction combined with strongly tunable offsets and temporal trajectories.**

Do not call this a universal “thermal-response manifold” without the local-domain qualifier.

## 7. Relation to prior art and novelty boundary

Prior literature already establishes that:
- polyurethane gelation/chemorheology depends on both temperature and formulation;
- urethane-prepolymer viscosity evolves with reaction time and is sensitive to PPG molecular weight, blend ratio, NCO/OH and synthesis temperature;
- PUR hot-melt industrial heat stability is commonly quantified through viscosity growth during molten thermal holding;
- broad polyurethane-prepolymer chemical spaces show composition-dependent temperature-viscosity parameters.

Relevant starting references:
- Haddadi, Nazockdast, Ghalei, *Polymer Engineering & Science* 2008, DOI: https://doi.org/10.1002/pen.21229
- “Application of the systemic rheology to the in situ follow-up of viscosity evolution with reaction time in the synthesis of urethane prepolymers”, *International Journal of Adhesion and Adhesives*, PII S0143749613002261
- Pugar et al., *Digital Discovery* 2025, DOI: https://doi.org/10.1039/D5DD00287G
- polyurethane reactive hot-melt heat-stability examples: https://patents.google.com/patent/WO2022035636A1/en and https://patents.google.com/patent/CN116134105A/en

Therefore the manuscript should **not** claim:
- first discovery that time and temperature both matter;
- first use of viscosity growth as a thermal-stability metric;
- composition-independent activation energy for polyurethane generally.

The paper can instead contribute the **local quantitative asymmetry** among rheological coordinates and connect that asymmetry to state-aware formulation decisions.

## 8. Manuscript consequence

The chemistry/rheology sequence should be:

1. **Temperature sweeps are highly structured rather than arbitrary.**  
   Seven realizations share a narrow apparent-Ea range and nearly collinear temperature-response vectors.

2. **Nominal formulation is insufficient to describe absolute rheological level.**  
   Same-formulation realization shifts reach 2.89-3.57x; realization-aware modeling sharply reduces residual error.

3. **Thermal-hold trajectory is a formulation-sensitive design coordinate.**  
   E1 and E5 differ strongly, and the corrected formulation suppresses 120 C drift over the matched window.

4. **Inverse formulation is therefore state-aware and constraint-based.**  
   A candidate should not be judged by one static viscosity prediction when process realization and hold trajectory can change the practical decision.

5. **The Agent is the decision layer, not the chemical discovery itself.**  
   It represents and audits this augmented state, recommends a point, and remains separated from human wet-lab actuation.

## 9. What is still missing if no further wet-lab work is possible?

No new experiment is required to **write** the paper or to support the local claims above.

The stronger statement that formulation-induced variance is generally concentrated in the temporal coordinate would benefit from matched time sweeps for more original formulations and independent batches. If those experiments cannot be performed, treat that as future validation and retain the current local wording.

The non-laboratory items still needed before submission are:

- freeze/attach the pre-result recommendation provenance if the final repeated measurement is called prospective;
- generate a reproducible table/figure for the temperature-slope and state-aware comparisons above;
- finish or deliberately scope the remaining formal Agent benchmark questions so manuscript claims match completed evidence;
- assemble manuscript v0.4 and perform a claim/provenance audit;
- ensure all statistics are generated from versioned data and not copied from prose.

## 10. Recommended headline claim

> **Reactive PUR in the studied local formulation space shows anisotropic rheological variability: experimental realization primarily shifts viscosity magnitude, formulation strongly changes thermal-hold trajectory, and the 80-130 C temperature-response slope remains comparatively conserved. This motivates state-aware inverse design in which formulation and process realization are evaluated jointly rather than through a single static viscosity target.**
