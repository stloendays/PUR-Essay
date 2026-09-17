# EXPERIMENTAL_RESULTS_V1

**Status:** authoritative experiment-first replacement text for the wet-lab part of the next manuscript revision.

## Proposed manuscript role

The laboratory study is the principal physical validation and closed-loop formulation result. Public rheology data, the frozen inverse-design benchmark, and the Agent evaluation provide context, decision logic, and auditability around this experimental core rather than replacing it.

## Results and Discussion — experimental mainline

### Prospective wet-lab validation tests transfer of the frozen local design

A local five-formulation matrix was constructed around a PPG2000/STEPANPOL PDP-70/4,4'-MDI system. The stoichiometric axis varied NCO:OH from 1.70 (E1) to 1.90 (E3) at a 50/50 PPG2000/PDP-70 polyol ratio, while the composition axis varied the polyol ratio from 60/40 (E4) to 40/60 (E5) at NCO:OH = 1.80. These experiments were executed after the formulation design had been defined and were not used to generate the frozen computational response surface. They therefore provide prospective external wet-lab validation of transfer from the computational design space to the laboratory system.

For every recorded run with a full temperature sweep, viscosity decreased monotonically between 80 and 130 C. The absolute viscosity level, however, was highly sensitive to experimental realization. The three recorded E2 runs (GJJ, ZYX, and CHH) gave values of 9462, 18780, and 27350 at 80 C and 1955, 4017, and 6977 at 120 C. The corresponding max/min spreads were 2.89-fold and 3.57-fold. A one-day retest also shifted the measured level for the available repeated samples. Thus, the laboratory validation did not simply confirm a single deterministic viscosity value; it exposed a substantial process-history/run-sensitivity dimension that was not represented by a static target-matching objective.

This discrepancy is scientifically useful rather than a failed validation. It identifies a distinction between **property targeting** and **formulation robustness**: a composition can occupy a desirable nominal viscosity region while still displaying unacceptable temporal or preparation sensitivity under process-relevant conditions.

### Thermal holding reveals a formulation-dependent viscosity-stability failure mode

The stability deficit became explicit when samples were held at 120 C. E1 increased from 708.7 at 15 min to 776.1 at 60 min and 828.1 at 90 min, corresponding to increases of 9.51% and 16.85%, respectively. E5 showed a much stronger response, increasing from 2210 at 15 min to 3349 at 60 min and 4267 at 90 min. These changes correspond to 51.54% over 15-60 min and 93.08% over 15-90 min.

The strong difference between E1 and E5 shows that time at temperature cannot be treated only as measurement metadata. Under the investigated conditions, it becomes a formulation-dependent response variable. Accordingly, the original inverse-design objective, which emphasized instantaneous or fixed-condition viscosity, was incomplete for practical processing stability.

We therefore define a simple experimental hold-stability descriptor for a fixed temperature T and time interval t0 -> t1,

```text
SI(T; t0,t1) = [eta(T,t1) - eta(T,t0)] / eta(T,t0).
```

For the matched 120 C, 15-60 min interval, SI = 0.0951 for E1 and 0.5154 for E5. This descriptor is not used retroactively to alter the frozen historical benchmark; instead, it is introduced as a new experimentally learned design criterion for subsequent workflow iterations.

### Failure-aware formulation correction suppresses viscosity build-up reproducibly

The experimental failure was interpreted as being consistent with an excessively high fraction of reactive material in the original resin/polyol phase. A correction was therefore introduced in which the PPG2000/PDP-70 reactive fraction was reduced and AC1920/TK100 components were added. The corrected formulation contained 39.60 parts PPG2000, 39.60 parts PDP-70, 17 parts AC1920, 5 parts TK100, and 20.19 parts MDI according to the supplied laboratory sheet.

The same corrected formulation was then measured in two repeat runs. At 120 C, replicate 1 gave 1230, 1189, 1203, and 1228 at 15, 30, 45, and 60 min; replicate 2 gave 1281, 1260, 1289, and 1320. Over the common 15-60 min interval, the two runs changed by -0.16% and +3.04%, respectively. The mean profile changed by only 1.47%. Across the four matched time points, the two-run coefficient of variation ranged from approximately 2.87% to 5.11%.

The key experimental result is therefore not that the initial AI-guided formulation was perfectly predicted. Rather, the prospective laboratory test discovered a stability failure mode, the workflow generated a chemically motivated correction, and repeated measurements of the corrected formulation showed that the time-dependent viscosity build-up was strongly suppressed. On the matched 15-60 min window, the corrected formulation remained near-flat while E1 increased by 9.51% and E5 by 51.54%.

This constitutes a closed-loop formulation result:

```text
computationally motivated formulation design
-> prospective wet-lab execution
-> failure-mode discovery
-> formulation correction
-> repeated wet-lab confirmation
-> revised stability-aware objective
```

The correction experiment is not described as a blind external validation because it was selected after observing the initial failure. It is instead a **closed-loop follow-up validation**. The initial E1-E5 measurements retain the role of prospective external wet-lab validation provided they remained excluded from fitting or selecting the frozen pre-experiment computational decision.

### Experimental feedback changes the design objective

The experiments imply that future formulation selection should distinguish at least three quantities: viscosity magnitude, temperature dependence, and hold stability. A generic next-generation objective can therefore be written as

```text
J_next = w_eta L_eta + w_T L_temperature + w_S L_stability + penalties(feasibility),
```

where `L_stability` is evaluated from an explicitly defined hold-stability metric such as SI. The current experiments do not justify selecting a universal numerical stability threshold for all polyurethane systems; they demonstrate why stability must be represented explicitly rather than assumed from a single viscosity measurement.

This experimental feedback does not invalidate the frozen PUR-FRONTIER benchmark. The benchmark answers a reproducibility question under a fixed historical objective and fixed candidate space. The wet-lab result answers a different and more physical question: which additional variable becomes necessary when that frozen decision is transferred to experiment? The answer from the present study is thermal hold stability/process-history sensitivity.

### Mechanistic interpretation and claim boundary

The observed stabilization is consistent with the working hypothesis that partially replacing the original fully reactive resin/polyol fraction reduces the effective concentration of reaction-capable components and thereby suppresses viscosity build-up during thermal holding. However, the present data directly establish rheological stabilization, not a molecular kinetic mechanism. No direct conversion measurement, NCO-consumption kinetics, or spectroscopic time series was collected in the supplied experiment. The manuscript should therefore use wording such as **"consistent with reduced effective reactive fraction"** rather than asserting that a specific chemical pathway has been proven.

## Figure priority for the revised paper

The wet-lab evidence should move ahead of the current computational frontier figures.

- **Figure 1:** study architecture, centred on prospective experiment -> failure -> correction -> repeated confirmation.
- **Figure 2:** measured 80-130 C viscosity sweeps, emphasizing monotonic temperature response and E2 run-to-run spread.
- **Figure 3:** 120 C hold-stability curves for E1 and E5 together with both corrected-formulation replicates; use the shared 15-60 min window for quantitative comparison and show the 90-min E1/E5 points without implying corrected-formulation measurements at 90 min.
- **Figure 4:** compact stability/repeatability summary: SI values, corrected replicate CV, and the transition from static target matching to stability-aware design.
- Later figures: source-grounded rheology, deterministic frontier/backward design, then the blinded Agent benchmark.

## Claim summary

**Directly supported by the supplied experimental sheet:**

- strong monotonic temperature dependence in each recorded 80-130 C sweep;
- large run-to-run/process sensitivity in the original E2 formulation;
- strong 120 C viscosity build-up in E1 and especially E5;
- near-flat 15-60 min viscosity response in two repeat runs of the corrected formulation;
- reproducibility of the corrected time profile at the level reported above.

**Interpretive, not directly mechanistically proven:**

- the original stability failure originates specifically from the 100% reactive soft-chain polyol/resin fraction;
- AC1920/TK100 suppress build-up specifically by lowering reaction kinetics rather than through another rheological or phase effect.

These interpretations may be discussed as the formulation rationale, but the manuscript should preserve the distinction between observed rheology and proposed mechanism.