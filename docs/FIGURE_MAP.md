# Manuscript Figure Map

## Figure 2 — Formulation-dependent temperature sensitivity of polyurethane prepolymer viscosity

**Scientific question:** Can temperature dependence be represented by a compact rheological state, and is the temperature sensitivity universal across formulations?

- **A.** Andrade-fitted viscosity trajectories for 39 experimental polyurethane prepolymers over 45–75 °C, normalized to each formulation's fitted viscosity at 75 °C. This range remains inside the source measurement interval.
- **B.** Distribution of per-formulation Andrade fit quality. The dashed line marks R² = 0.98; 37/39 formulations exceed this threshold.
- **C.** Apparent flow activation energy, Ea,app, by polyol code. The broad 34.74–94.15 kJ mol⁻¹ range demonstrates formulation-specific thermal sensitivity.

**Main result:** Melt viscosity is approximately Andrade-like for most formulations, but a single universal temperature-shift factor is not defensible. A useful formulation state is therefore `(eta_ref, Ea,app)` rather than viscosity at one arbitrary temperature.

**Evidence role:** Experimental academic dataset (Pugar et al., Digital Discovery 2025). No PUR_SIM_V1 values are used.

---

## Figure 3 — Free-NCO level couples viscosity magnitude and thermal sensitivity

**Scientific question:** Does free NCO act only as an intercept-like viscosity control, or does it also alter the temperature response?

- **A.** Within-chemistry viscosity multiplier per +1 wt%-point free NCO for 11 chemistry families whose Andrade fits all satisfy R² >= 0.98, evaluated at 45 and 75 °C within the source range. Median multipliers are approximately 0.709 and 0.736.
- **B.** Change in apparent activation energy per +1 wt%-point free NCO. Ea,app decreases in 9/11 high-quality families.
- **C.** Direct comparison of 45 and 75 °C multipliers. Points below the identity line indicate stronger NCO-induced viscosity reduction at lower temperature.

**Main result:** Increasing free NCO systematically lowers prepolymer viscosity and commonly alters apparent thermal sensitivity. Stoichiometric state therefore changes both viscosity level and temperature response.

**Evidence role:** Matched chemistry-family analysis within the experimental Pugar dataset.

---

## Figure 4 — Temperature amplification, rank reversal and composition-context interaction

**Scientific question:** Are chemistry effects transferable across temperature and blend context, or can both contrast magnitude and ordering change?

- **A.** Seven matched C-versus-P comparisons at identical isocyanate and free-NCO level, evaluated at 45 and 75 °C inside the source range. The median chemistry contrast is substantially larger at lower temperature.
- **B.** Pair-specific low-temperature amplification `(C/P)45 / (C/P)75`, showing systematic amplification of chemistry contrast on cooling.
- **C.** Approximately controlled 2×2 composition block from US5932680A Examples 5–8 at NCO:OH = 1.4. The High-A/Low-A viscosity ratio is 1.654× in a C/D-balanced background but 1.091× in a D-rich background; ratio-of-ratios = 1.516.
- **D.** Direct patent rank reversal: US5932680A Example 1 versus Example 4 changes from 190 > 98 Pa·s at 90 °C to 55 < 60 Pa·s at 110 °C.

**Main result:** Temperature is not only a scalar viscosity-shift variable. It can amplify chemistry contrast and, in published examples, reverse formulation ordering. Composition effects are also context-dependent, supporting a non-additive formulation response.

**Evidence role:** Panels A–B use source-range Pugar-derived matched comparisons. Panels C–D use published patent point values. Panel C is an effect-size interaction only because replicate variance is not reported.

---

## Figure 5 — Constraint-induced decision phase transitions and nominal-to-robust rank inversion

**Scientific question:** How does a property optimum become a deployable formulation decision, and is the final choice stable to formulation constraints?

- **A.** All 928 frozen PUR_SIM_V1 candidates in property-score versus MDI-fraction space. The L0 property optimum `WO_INV_0419` lies at 34.06% MDI, below the frozen 35% floor. Backward feasibility gives NCO:OH ≈ 1.772 and the first reachable 0.1-grid state at 1.8.
- **B.** Decision phase map obtained by continuously varying only the MDI lower bound. Nominal and robust winners undergo discrete formulation transitions, showing that the 35% gate lies inside a genuine decision-boundary region rather than acting as a cosmetic filter.
- **C.** Nominal versus robust ranks for the 117 robust-admissible candidates. Global ordering remains strongly preserved (Spearman ≈ 0.985), yet 367/6786 pairs invert and the Top-1 decision changes from `WO_INV_0579` to `WO_INV_0420`. A fixed-chemistry control shows zero inversions.

**Main result:** Decision-frontier inversion occurs despite strong global rank preservation. Constraint propagation and robustness change the decision-critical head of the ranking without implying global failure of the response surface.

**Evidence role:** Hash-verified synthetic `PUR_SIM_V1` benchmark; algorithmic decision geometry, not experimental polyurethane evidence.

---

## Figure 6 — Uncertainty phase diagram, robustness cliff and objective-geometry sensitivity

**Scientific question:** How much uncertainty is required to change the winner, when does the robust design space disappear, and how sensitive is the decision to the mathematical definition of rheological state?

- **A.** Winner phase diagram as the frozen candidate-specific log-uncertainty radius is scaled by `s`. The nominal winner `WO_INV_0579` crosses to `WO_INV_0420` at `s ≈ 0.364`; further uncertainty produces additional winner phases.
- **B.** Number of broad-window robust-admissible candidates versus uncertainty scale. At the frozen `s = 1`, 117 candidates remain; the feasible set collapses at `s ≈ 1.806`, with viscosity ratio / thermal sensitivity as the terminal bottleneck.
- **C.** Winner-frequency basins from 50,000 random objective-weight vectors. `WO_INV_0579` dominates the nominal basin (~79.8%), whereas the robust landscape is more distributed, led by `WO_INV_0420` (~44.2%) and `WO_INV_0341` (~36.3%).
- **D.** Frozen three-term robust rank versus an independent two-degree-of-freedom rheology-state robust rank. Because `eta80 = eta120 × ratio`, the original three-term objective induces a 3:1 principal metric anisotropy; the alternative state definition substantially reorders the robust frontier and changes L2 from `WO_INV_0420` to `WO_INV_0404`.

**Main result:** Robust formulation selection is characterized by identifiable uncertainty-driven phase transitions, a finite robustness cliff and non-trivial objective-geometry sensitivity. The workflow therefore reports decision stability regions rather than treating a single optimum as universally invariant.

**Evidence role:** Hash-verified synthetic `PUR_SIM_V1` benchmark; algorithmic sensitivity analysis only.

---

## Placement in the manuscript

1. **Figure 1:** overall evidence → rheology science → deterministic frontier → backward design → blind Agent → prospective validation workflow.
2. **Figure 2:** within-range temperature law and formulation-specific Ea,app.
3. **Figure 3:** free-NCO coupling to viscosity magnitude and thermal sensitivity.
4. **Figure 4:** lower-temperature chemistry amplification, direct temperature-driven rank reversal and composition-context interaction.
5. **Figure 5:** constraint phase transition and nominal-to-robust decision-frontier inversion.
6. **Figure 6:** uncertainty phase diagram, robustness cliff and objective-geometry sensitivity.
7. **Figure 7:** blind Agent complete-decision recovery.
8. **Figure 8:** prospective wet-lab validation.
