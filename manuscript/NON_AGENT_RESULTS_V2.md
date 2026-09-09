# Non-Agent Results V2 — authoritative replacement text for the deterministic paper core

This document supersedes the older 80/120 °C source-derived wording in manuscript v0.3. It is designed to be merged into manuscript v0.4. Experimental/public evidence and PUR_SIM_V1 benchmark evidence are intentionally separated.

## 2.2 Temperature dependence is compact but formulation-specific

The densest experimental subset comprises 39 polyurethane prepolymers and 4,559 usable temperature–viscosity observations from the Pugar et al. dataset. Each formulation was fitted independently to an Andrade-type relation,

ln(η) = A + B/T,

with apparent flow activation energy defined as Ea,app = RB. The median formulation-level R² was 0.9967 and 37/39 formulations exceeded R² = 0.98. Thus, over the source measurement range, the temperature response of an individual formulation is well compressed by a low-dimensional state.

The fitted curve shape is simple, but its magnitude is not universal. Ea,app spans 34.74–94.15 kJ mol⁻¹, with a median of 51.09 kJ mol⁻¹. This range is too large to justify a single formulation-independent temperature shift factor. A more informative processing state is therefore (ηref, Ea,app): one coordinate specifies viscosity magnitude, while the second specifies thermal sensitivity.

Figure 2 is restricted to 45–75 °C, which lies inside the experimental source range. The figure therefore shows within-range fitted/interpolated response rather than 120 °C extrapolation.

**Result:** approximately Andrade-like temperature response does not imply universal temperature dependence; thermal sensitivity is itself a formulation property.

## 2.3 Free NCO alters both viscosity magnitude and thermal sensitivity

To isolate stoichiometric effects from chemistry changes, free-NCO trends were analyzed within matched polyol/isocyanate families. Eleven families were retained for the high-quality analysis because every underlying formulation had Andrade R² ≥ 0.98.

Increasing free NCO lowered fitted viscosity in all 11 high-quality families at both 45 and 75 °C. Per +1 wt%-point free NCO, the median viscosity multipliers are approximately 0.709 at 45 °C and 0.736 at 75 °C. The stronger reduction at the lower temperature is consistent with the simultaneous change in temperature sensitivity. The median dEa,app/dNCO is approximately −0.81 kJ mol⁻¹ per wt%-point free NCO, and 9/11 families show a negative slope.

The effect is heterogeneous rather than universal: the 45 °C multiplier spans approximately 0.597–0.955 across the retained chemistry families. This heterogeneity is scientifically important because it implies that stoichiometry cannot be represented as one chemistry-independent viscosity correction.

**Result:** free NCO is not merely an intercept-like control of melt viscosity; it changes both the viscosity level and the thermal sensitivity, with family-specific effect magnitude.

## 2.4 Temperature amplifies chemistry contrast and can reverse formulation order

Matched C-versus-P comparisons were constructed at identical isocyanate identity and free-NCO level. For seven direct matched pairs, the median C/P viscosity contrast is approximately 8.85 at 45 °C and 4.63 at 75 °C. The median low-temperature amplification,

(C/P)45 / (C/P)75,

is approximately 1.91. Thus, chemistry differences do not propagate as a temperature-independent ratio: cooling systematically increases the rheological separation in this matched set.

This behavior has a stronger qualitative consequence. In the experimental Pugar-derived response manifold, formulation rankings at 45 and 75 °C remain globally similar, yet local pairwise order can change. The strongest direct source-level confirmation comes from US5932680A: Example 1 and Example 4 satisfy 190 > 98 Pa·s at 90 °C but 55 < 60 Pa·s at 110 °C. This is a genuine temperature-induced rheological rank reversal using published point values, not an extrapolated model crossing.

**Result:** temperature is not only a scalar viscosity-shift variable. It can magnify chemistry contrast and can change which formulation is more viscous.

## 2.5 Composition effects depend on formulation context

US5932680A Examples 5–8 provide an approximately controlled 2×2 composition block. At 130 °C, the same directional A/B polyester change produces a High-A/Low-A viscosity ratio of 43/26 = 1.654 in a C/D-balanced background but only 24/22 = 1.091 in a D-rich background. The ratio-of-ratios is therefore 1.516.

Because replicate-level variance is not reported, this result is interpreted strictly as an effect-size interaction rather than a statistical significance test. Nevertheless, the magnitude of the interaction is inconsistent with a universal additive picture in which the rheological contribution of one component is independent of the surrounding blend.

A more realistic formulation mapping is therefore

η = f(composition, stoichiometry, temperature, interactions),

rather than an additive sum of independent component coefficients.

**Result:** the rheological effect of a composition change is context-dependent, providing source-grounded evidence for non-additive formulation coupling.

---

# Deterministic decision layer: PUR_SIM_V1

The following results are algorithmic properties of the synthetic PUR_SIM_V1 benchmark. They are not presented as experimental polyurethane laws. The complete 928-row response table is losslessly reconstructed from the historical PUR_SIM_V1 snapshot and SHA256-verified before analysis.

## 2.6 Property optimum, constrained optimum and robust optimum are distinct decisions

The frozen benchmark contains 58 polyol blends × 16 NCO:OH values = 928 candidates. The three-layer decision chain is:

- L0 property optimum: WO_INV_0419.
- L1 nominal constrained optimum: WO_INV_0579.
- L2 worst-case-interval robust optimum: WO_INV_0420.

WO_INV_0419 is a 50/50 PPG700/PPG1000 formulation at NCO:OH = 1.7. It is closest to the frozen rheological target but contains only 34.06% MDI on the polyol+MDI mass basis, below the frozen 35% lower limit. The most target-like point is therefore not the deployable decision.

L1 applies point-response preferred/broad windows, NCO:OH, MDI-fraction and chemistry-domain constraints and leaves 141 nominally feasible candidates. L2 propagates candidate-specific log-space uncertainty, requires full intervals to remain inside broad functional windows and ranks the 117 robust-admissible candidates by the exact worst-case extension of the same frozen objective.

**Result:** property optimization, feasibility and robustness select different formulations even when they operate on one frozen candidate set.

## 2.7 The MDI constraint creates a decision phase transition rather than a simple filter

Backward analysis on the L0 blend gives a continuous MDI feasibility threshold at NCO:OH = 1.77198. On the frozen 0.1 grid, the first reachable state is NCO:OH = 1.8, corresponding to WO_INV_0420.

A deeper phase-map analysis varies only the assumed lower MDI bound. The nominal winner passes through discrete regimes including WO_INV_0419 → WO_INV_0659 → WO_INV_0579, while the robust decision follows a different sequence including WO_INV_0419 → WO_INV_0436 → WO_INV_0659 → WO_INV_0420. The operational 35% boundary lies inside these transition regimes.

Thus, the 35% condition is not merely removing one otherwise-optimal point. It changes the identity of the decision optimum over a finite region of the constraint axis.

**Result:** formulation constraints generate constraint-induced decision phases, and backward design locates the boundary at which the identity of the preferred formulation changes.

## 2.8 Robust propagation preserves the global ranking while inverting the decision frontier

Across the 117 robust-admissible candidates, nominal and robust rankings remain strongly correlated:

Spearman ρ = 0.9851,
Kendall τ = 0.8918.

Nevertheless, 367 of 6,786 pairwise relations invert (5.41%), and the Top-1 decision changes from WO_INV_0579 to WO_INV_0420. A fixed 50/50 PPG700/PPG1000 NCO:OH control over 1.8–2.5 gives τ ≈ 1.0 and 0/28 pairwise inversions.

The control is important: interval propagation does not mechanically manufacture a ranking change. Instead, inversion is concentrated where target distance, formulation feasibility, domain support and uncertainty compete near the decision frontier.

**Result:** the scientifically relevant phenomenon is decision-frontier inversion despite strong global rank preservation, not global collapse of the screening landscape.

## 2.9 Uncertainty produces its own winner phases and a finite robustness cliff

The frozen candidate-specific uncertainty radius was multiplied by a common scale s while leaving all nominal responses, constraints and objective weights unchanged. At s = 0 the robust criterion reduces toward the nominal ranking and WO_INV_0579 is selected. The exact score crossover between WO_INV_0579 and WO_INV_0420 occurs at s ≈ 0.3637. WO_INV_0420 then dominates a broad interval around the frozen s = 1, after which additional robust winner phases appear.

The number of broad-window robust-admissible candidates decreases continuously with uncertainty. The final admissible region disappears at s ≈ 1.8063. The terminal limiting coordinate is the η80/η120 ratio, i.e. the thermal-sensitivity coordinate.

This defines a finite robustness cliff: above a calculable uncertainty level, the correct outcome is not to choose a new nominal winner but to report that no candidate can be robustly certified within the frozen broad processing envelope.

**Result:** robustness is a phase diagram with a finite loss-of-feasibility boundary, not a binary label attached to one optimum.

## 2.10 The nominal optimum has a broad objective basin, whereas the robust optimum lies on a richer trade-off frontier

To test sensitivity to the relative importance assigned to η80, η120 and η80/η120, 50,000 objective-weight vectors were sampled over the three-component weight simplex. WO_INV_0579 remains the nominal winner for approximately 79.8% of sampled weights. The nominal optimum therefore occupies a broad stability basin rather than depending on one finely tuned equal-weight choice.

The robust landscape is more distributed. WO_INV_0420 is selected for approximately 44.2% of sampled weight vectors and WO_INV_0341 for approximately 36.3%, with smaller basins occupied by several additional candidates. Separately, 44 of the 117 robust-admissible candidates are non-dominated when target deviations, uncertainty radius and domain ratio are treated as independent Pareto objectives.

The appropriate interpretation is therefore:

Pareto opportunity set → declared decision functional → unique decision under the frozen rule.

**Result:** the frozen robust winner is auditable and reproducible, but the underlying opportunity set contains a genuine multi-objective trade-off structure that should not be hidden behind a single scalar score.

## 2.11 Objective geometry reveals an implicit metric choice in the three-term rheology target

The three frozen target coordinates are algebraically dependent because

η80 = η120 × (η80/η120).

Thus the response has only two independent temperature-response degrees of freedom. Let

u = log10(η120/η120*)

and

v = log10[(η80/η120)/(η80/η120)*].

The equal-weight three-term objective induces the two-dimensional quadratic metric

[[2, 1],
 [1, 2]],

whose eigenvalues are 3 and 1. Therefore, the original objective implicitly weights one principal direction three times more strongly than the orthogonal direction.

This does not invalidate the frozen benchmark; the frozen definition remains the primary decision rule. It does, however, motivate an objective-geometry sensitivity analysis. When the rheological state is represented directly by two independent normalized coordinates—reference viscosity and thermal sensitivity—the robust ranking is substantially reordered (Spearman correlation with the frozen robust rank ≈ 0.428), and the alternative-state L2 winner becomes WO_INV_0404 rather than WO_INV_0420.

**Result:** robust formulation choice depends not only on uncertainty magnitude but also on how an intrinsically two-dimensional rheological state is embedded into an objective function. Decision papers should therefore report objective geometry, not only a scalar optimum.

## 2.12 The synthetic benchmark exposes a prospective physical hypothesis rather than pretending to be the physical law

PUR_SIM_V1 imposes an almost blend-invariant stoichiometric sensitivity: across all 58 blend trajectories, d ln η80/d(NCO:OH), d ln η120/d(NCO:OH) and dEa/d(NCO:OH) are effectively constant to numerical precision. Real matched-family evidence is more heterogeneous: the experimental free-NCO viscosity response varies substantially across chemistry families and the sign/magnitude of dEa/dNCO is not universal.

Free-NCO wt% and NCO:OH are not identical variables, so their numerical slopes must not be directly equated. The structural contrast nevertheless yields a strong prospective hypothesis:

**chemistry × stoichiometry interaction:** the rheological sensitivity to stoichiometric change in real polyurethane prepolymers is itself chemistry-dependent.

The prospective wet-lab program should therefore test not only whether the selected formulation lands in the target window, but whether NCO:OH response slopes differ across neighboring PPG700/PPG1000 compositions. A confirmed slope interaction would convert a limitation of the synthetic benchmark into an experimentally supported materials-science result.

---

# Claim boundary

1. Sections 2.2–2.5 are supported by experimental academic data and/or direct patent values.
2. 45/75 °C Pugar-derived comparisons lie inside the source range; they replace the older 80/120 °C manuscript language that included extrapolation to 120 °C.
3. Sections 2.6–2.12 concerning the 928-candidate frontier are properties of the synthetic PUR_SIM_V1 benchmark.
4. PUR_SIM_V1 may support finite-space decision, robustness, phase-map, reachability and Agent-benchmark claims, but not experimental physical-law claims.
5. Agent performance is evaluated only after deterministic gold is frozen.
6. Prospective experiments remain the independent test of physical transferability.
