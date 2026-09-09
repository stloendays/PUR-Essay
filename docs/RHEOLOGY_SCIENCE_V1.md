# PUR-RHEOLOGY V1 — source-grounded rheology science layer

## Purpose

This module is the non-Agent scientific core of the PUR study. It uses only experimental/public evidence from the HMPUR database. Synthetic `PUR_SIM_V1` candidate responses are excluded from empirical rheology claims and remain an algorithmic benchmark only.

The central question is not merely which formulation ranks first. It is:

> How do formulation chemistry, free NCO level and temperature jointly control prepolymer viscosity, and which response coordinates remain comparable across heterogeneous public sources?

## 1. Public viscosity evidence is protocol-heterogeneous

The normalized database currently contains 70 melt-viscosity observations from 10 independent sources. Reported temperatures span 25, 90, 100, 110, 120, 121 and 130 °C, and reported units include Pa·s, mPa·s and cP.

Therefore raw cross-source viscosity values must not be pooled as if they were measured under one protocol. Source, temperature and method remain explicit evidence fields.

## 2. Temperature dependence is well represented by an Andrade state variable

The Pugar experimental library contributes 39 polyurethane prepolymers and 4559 temperature-viscosity points in the SQLite database. Each sample was fit independently to

`ln(eta) = A + B/T`

with apparent activation energy

`Ea = R B`.

Results:

- median fit R² = **0.9967**;
- **37/39** samples have R² >= 0.98;
- median apparent Ea = **51.09 kJ/mol**;
- observed Ea range = **34.74–94.15 kJ/mol**.

Independent patent formulations in US5932680A show the same approximate temperature-law behavior over 90–130 °C for the three examples with three reported temperatures:

- Example 1: Ea = **65.72 kJ/mol**, R² = **0.9968**;
- Example 2: Ea = **60.14 kJ/mol**, R² = **0.9999**;
- Example 3: Ea = **75.55 kJ/mol**, R² = **0.9971**.

### Scientific implication

A single universal temperature correction factor is not defensible: the temperature sensitivity itself is formulation-dependent. A more useful rheological state representation is therefore a reference-temperature viscosity plus an apparent activation energy, for example `(eta120, Ea)`, rather than viscosity at one arbitrary temperature.

## 3. Increasing free NCO lowers viscosity and usually weakens temperature sensitivity

Thirteen matched polyol/isocyanate chemistry families contain at least two free-NCO levels. Across all 13 families, fitted eta80 decreases as %NCO increases; eta120 decreases in 12/13. Restricting to the 11 families whose every Andrade fit has R² >= 0.98, both eta80 and eta120 decrease in **11/11** families.

For those 11 high-quality families, the median effect of +1 percentage point free NCO is:

- eta80 multiplier = **0.742** (about **25.8% lower**);
- eta120 multiplier = **0.783** (about **21.7% lower**);
- apparent Ea change = **−0.81 kJ/mol per %NCO**;
- Ea decreases in **9/11** families.

### Scientific implication

Free NCO is not merely an intercept-like viscosity control. Its effect is somewhat stronger at 80 °C than at 120 °C and commonly reduces the apparent activation energy. Stoichiometry therefore changes both the absolute viscosity and the thermal sensitivity of the prepolymer.

## 4. Lower temperature amplifies chemistry contrast

For matched Pugar formulations using the same diisocyanate (4,4'-MDI or Mondur MLQ) and the same %NCO, seven direct C-versus-P polyol comparisons are available.

Across these matched comparisons:

- median C/P viscosity ratio at 80 °C = **4.20**;
- median C/P viscosity ratio at 120 °C = **2.06**;
- median low-temperature amplification = **1.99×**;
- median Ea(C) − Ea(P) = **+19.89 kJ/mol**.

### Scientific implication

Chemistry differences do not remain constant across temperature. In these matched comparisons, the same C-versus-P polyol contrast is approximately twice as large at 80 °C as at 120 °C. This provides direct experimental evidence that temperature can amplify formulation contrast rather than simply shifting every formulation by the same factor.

## 5. HMPUR patent data show a composition-context interaction at fixed NCO:OH

US5932680A Examples 5–8 form an approximately controlled 2×2 block at NCO:OH = 1.4 with closely matched PPG425, tackifier and MDI loadings.

At 130 °C:

| Background | Low-A state | High-A state | High-A / Low-A |
|---|---:|---:|---:|
| C/D balanced | 26 Pa·s | 43 Pa·s | **1.654×** |
| D-rich | 22 Pa·s | 24 Pa·s | **1.091×** |

The ratio-of-ratios is **1.516**, corresponding to a log interaction contrast of **0.416**.

### Scientific implication

The rheological effect of the A/B composition shift depends strongly on the surrounding polyester context. The available published point values therefore support a **context-modulated, non-additive formulation response** after prepolymer formation.

This is an effect-size statement only. The patent does not provide replicate variance for these four points, so no inferential p-value is claimed.

## 6. Revised non-Agent scientific model

The recommended deterministic scientific workflow is now:

```text
source/protocol audit
    -> per-formulation temperature normalization
    -> rheological state (eta_ref, Ea)
    -> within-chemistry stoichiometry trends
    -> matched chemistry-contrast analysis
    -> local formulation-interaction analysis
    -> constrained / robust design frontier
    -> backward reachability
    -> prospective wet-lab validation
```

The Agent sits outside this chain and is evaluated later on whether it can recover the frozen scientific decision state.

## 7. Manuscript-level claims supported now

1. **Temperature dependence is mostly Andrade-like but formulation-specific.**
2. **A universal temperature shift factor is invalid because apparent activation energy varies strongly across chemistries.**
3. **Higher free NCO systematically lowers prepolymer viscosity and commonly lowers temperature sensitivity.**
4. **Lower temperature amplifies chemistry-dependent viscosity contrast.**
5. **The effect of a polyester composition change is context-dependent, consistent with non-additive rheological coupling.**

These claims are source-grounded and do not depend on the Agent benchmark.

## Evidence boundary

- Pugar continuous curves: experimental academic data; sample mapping and synthesis details from Pugar et al., *Digital Discovery* 2025, DOI 10.1039/D5DD00287G.
- US5932680A: published patent point values; used as historical evidence without assuming zero measurement error.
- `PUR_SIM_V1`: synthetic deterministic candidate table; excluded from empirical science claims above.
