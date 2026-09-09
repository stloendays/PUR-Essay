# PUR-FRONTIER-DEPTH V1

This layer **does not replace or retune PUR-FRONTIER V1**. It asks a deeper question: once the frozen winner chain is reproducible, what is the geometry of the decision itself? The analysis treats MDI feasibility, uncertainty strength, objective geometry and multiobjective trade-offs as independent axes and reports when the selected formulation changes.

## 1. Frozen decision chain is reproduced

Using the recovered 928-row PUR_SIM_V1 table:

```text
L0 property-only       WO_INV_0419
L1 nominal constrained WO_INV_0579
L2 minimax robust      WO_INV_0420
```

There are 141 nominal-feasible candidates and 117 robust-admissible candidates under the frozen FRONTIER V1 definition.

For the 117-candidate comparison set, nominal and robust ranks remain globally similar:

```text
Spearman rho = 0.9851
Kendall tau  = 0.8918
367 / 6786 pairwise inversions = 5.41%
```

Yet Top-1 changes from `WO_INV_0579` to `WO_INV_0420`. A fixed 50/50 PPG700/PPG1000 NCO:OH sweep from 1.8 to 2.5 is a rank-preservation control with Kendall tau approximately 1 and 0/28 inversions. Thus robust propagation does not mechanically reorder every comparison; inversion is concentrated at the decision frontier.

## 2. Manufacturing constraint creates a decision phase map

The 35 wt% MDI lower bound should not be described as a simple post-hoc filter. Sweeping the bound reveals piecewise-stable decision regions.

Nominal property decision near the operational boundary:

```text
MDI floor <= 34.0625%          WO_INV_0419
34.0625% < floor <= 34.5868%   WO_INV_0659
34.5868% < floor <= 35.6107%   WO_INV_0579
```

Robust decision near the same boundary:

```text
MDI floor <= 34.0625%          WO_INV_0419
34.0625% < floor <= 34.5408%   WO_INV_0436
34.5408% < floor <= 34.5868%   WO_INV_0659
34.5868% < floor <= 35.3577%   WO_INV_0420
```

At the frozen 35% floor, the nominal and robust decisions therefore occupy different phases. This is a **constraint-induced decision phase transition**, not merely a feasibility count.

The backward calculation on the 50/50 PPG700/PPG1000 trajectory remains exact: the continuous MDI-floor crossing is NCO:OH approximately 1.772, and projection onto the 0.1 grid gives 1.8 (`WO_INV_0420`).

## 3. Uncertainty strength creates a second phase axis

Let `s` multiply the frozen candidate uncertainty radius while leaving nominal responses fixed. The minimax score is then a quadratic function of `s`, while broad-window robust admissibility disappears at candidate-specific thresholds.

The first score crossover between the frozen L1 and L2 winners occurs at:

```text
s = 0.363698
```

so uncertainty must reach only ~36% of its frozen magnitude before `WO_INV_0420` overtakes `WO_INV_0579` on minimax score.

The winner sequence then becomes a robustness relay. Approximate intervals are:

```text
s = 0        to 0.3637   WO_INV_0579
s = 0.3637   to 1.3616   WO_INV_0420
s = 1.3616   to 1.4987   WO_INV_0437
s = 1.4987   to 1.6384   WO_INV_0454
s = 1.6384   to 1.6705   WO_INV_0470
s = 1.6705   to 1.7384   WO_INV_0455
s = 1.7384   to 1.8063   WO_INV_0440
s > 1.8063                no broad-window robust candidate
```

After the first score crossover, most later transitions are caused by **admissibility cliffs** rather than another score crossover: the current winner's uncertainty interval reaches a broad processing boundary and drops out.

The entire robust set becomes unreachable at `s = 1.8063`; the last surviving candidate is `WO_INV_0440`, with the ratio/thermal-sensitivity coordinate as the limiting boundary.

## 4. Strict preferred-window certification is a separate reachability problem

Full uncertainty-interval containment inside all preferred windows is intentionally not the L2 gate. Evaluated as a stricter certification diagnostic, it has zero feasible candidates at the frozen uncertainty scale.

Among the 141 nominal-feasible candidates, the best uniform uncertainty scale for strict preferred-window certification is:

```text
WO_INV_0374: s_max = 0.655996
```

which means at least a 34.40% uniform uncertainty reduction would be required before any candidate could receive that stronger certification.

The limiting coordinate is:

```text
ratio / thermal sensitivity : 124 / 141 candidates
eta120                      : 16 / 141
eta80                       : 1 / 141
```

Thus thermal-sensitivity uncertainty is a systematic certification bottleneck, not an isolated property of one formulation.

## 5. The original three response terms live on a two-dimensional manifold

The frozen response coordinates obey the identity:

```text
eta80 = eta120 * (eta80/eta120)
```

so `{eta80, eta120, ratio}` are a redundant embedding of a two-degree-of-freedom rheology state. Writing

```text
u = log10(eta120 / eta120*)
v = log10(ratio / ratio*)
```

makes the eta80 deviation approximately `u + v + delta`, with `delta = -0.00235` because the independently chosen geometric centres are nearly, but not exactly, multiplicatively consistent.

The equal-weight three-term objective therefore induces the quadratic metric

```text
[[2, 1],
 [1, 2]]
```

on `(u, v)`. Its eigenvalues are 3 and 1, so one principal direction is implicitly weighted three times more strongly than the orthogonal direction even before any explicit user weighting is introduced.

This is not an error in frozen FRONTIER V1; it is an **objective-geometry result**. As a structural sensitivity analysis, a normalized two-coordinate state using eta120 level plus ratio/thermal sensitivity gives:

```text
state L0 = WO_INV_0419
state L1 = WO_INV_0420
state L2 = WO_INV_0404
```

These are not replacements for the frozen gold. They show that formulation choice depends on the declared metric on the physically two-dimensional rheology manifold.

## 6. Weight-stability basin, not a single magic winner

To quantify stability of the scalarization itself, 50,000 Dirichlet(1,1,1) weight vectors were sampled over the three frozen response terms while keeping all hard gates fixed.

Nominal L1 winner frequencies were approximately:

```text
WO_INV_0579 79.85%
WO_INV_0420 10.19%
WO_INV_0341  6.33%
```

Robust L2 winner frequencies were approximately:

```text
WO_INV_0420 44.15%
WO_INV_0341 36.25%
WO_INV_0470  5.68%
WO_INV_0404  5.46%
```

`WO_INV_0420` is therefore the unique winner under the frozen equal-weight minimax rule, while the broader analysis reports its **objective-stability basin** rather than pretending that all plausible scalarizations must choose the same formulation.

## 7. Pareto structure exposes the underlying trade-off surface

Using five minimization coordinates—absolute log-distance in eta80, eta120 and ratio, uncertainty radius, and chemistry-domain ratio—44 of the 117 robust-admissible candidates are non-dominated.

This is scientifically useful rather than problematic. The Pareto set is the underlying trade-off surface; the frozen decision functional selects one reproducible point on it. The paper can therefore separate:

```text
multiobjective opportunity set -> frozen decision rule -> unique selected candidate
```

instead of conflating Pareto optimality with a unique physical optimum.

## 8. Synthetic model structure itself should be audited

Across all 58 blends in PUR_SIM_V1, the synthetic NCO:OH derivative is essentially identical by construction:

```text
d ln(eta80) / d(NCO:OH)  = -0.261398 for all 58 blends
d ln(eta120) / d(NCO:OH) = -0.400000 for all 58 blends
d Ea_app / d(NCO:OH)     = +4.000 kJ mol-1 per NCO:OH unit for all 58 blends
```

By contrast, the source-derived Pugar high-quality families show substantial family-to-family heterogeneity in the effect of free NCO. At 45 C, the per-+1 wt%-point viscosity multiplier spans approximately 0.597-0.955 across 11 families; the corresponding apparent-Ea slope is negative in 9/11 families and ranges from about -3.15 to +0.23 kJ mol-1 per wt%-point.

NCO:OH and free-NCO wt% are not the same coordinate, so these magnitudes must not be directly calibrated against one another. The legitimate conclusion is structural: **the synthetic benchmark intentionally under-resolves chemistry x stoichiometry interaction relative to the heterogeneity seen in source data.** This becomes a prospective validation target rather than a reason to discard the benchmark.

## Paper-level interpretation

The strengthened non-Agent story is therefore not "we found one optimum from 928 points". It is:

```text
real-data rheology heterogeneity
-> finite synthetic response benchmark
-> constraint-induced decision phase transition
-> uncertainty-induced ranking inversion
-> robustness cliff and certification reachability
-> objective-manifold sensitivity
-> Pareto opportunity set
-> backward projection to an experimentally testable formulation
```

Agent evaluation remains downstream and blind. It is tested on whether it recovers this frozen decision chain, not used to create the scientific conclusions above.

## Claim boundary

Physical rheology trends come from source measurements and the prospective experiment. PUR_SIM_V1 supports deterministic algorithmic findings about ranking, phase boundaries, robustness, reachability and decision geometry. The two evidence layers are intentionally connected but never conflated.
