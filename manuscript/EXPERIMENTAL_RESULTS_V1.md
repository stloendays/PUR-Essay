# EXPERIMENTAL_RESULTS_V1

**Status:** authoritative experiment-first replacement text for the wet-lab part of the next manuscript revision.

## Proposed manuscript role

The laboratory study is the principal physical validation of an **uncertainty-aware, human-in-the-loop formulation workflow**. The scientific Agent is not presented as a laboratory actuator. Its role is to quantify decision uncertainty, recommend informative/robust formulation and measurement points, and issue an auditable decision before measurement. Human operators then execute the chemistry and rheology experiment. The final experiment therefore tests the quality of the Agent recommendation rather than an ability of the Agent to manipulate laboratory hardware.

Public rheology data, the frozen inverse-design benchmark, and the PUR-RECOVER benchmark provide physical context, deterministic decision logic, and an independent audit of reasoning reproducibility around this experimental core.

## Results and Discussion — experimental mainline

### The design state includes chemistry and process history

The experimental design is represented by two variable blocks rather than composition alone:

```text
x_chem = formulation variables
z_proc = {reaction_history, thermal_hold_time, preparation_perturbation}

y = rheology(x_chem, z_proc)
```

Reaction history, hold time, and preparation perturbation are not claimed here as newly discovered physical factors. They are known process-relevant variables that were not yet operationalized as explicit coordinates in the original static viscosity-targeting objective. The role of the wet-lab study is to quantify their importance in the present formulation system and provide observations that allow these variables to enter the next design iteration.

This distinction changes the interpretation of experimental variability. Run-to-run and time-at-temperature changes are not merely nuisance error around a single deterministic viscosity. They are measurements of a process-state response that the Agent must account for through uncertainty/robustness assessment when recommending experimental points.

### Agent-guided prospective wet-lab validation tests transfer of the local design

A local five-formulation matrix was constructed around a PPG2000/STEPANPOL PDP-70/4,4'-MDI system. The stoichiometric axis varied NCO:OH from 1.70 (E1) to 1.90 (E3) at a 50/50 PPG2000/PDP-70 polyol ratio, while the composition axis varied the polyol ratio from 60/40 (E4) to 40/60 (E5) at NCO:OH = 1.80.

The digital layer evaluates candidates and uncertainty; it does not physically synthesize or measure them. Experimental points/conditions recommended before measurement are passed to a human operator for execution. In paper-facing terminology, this is **Agent-guided experimental design with human wet-lab actuation**.

For every recorded run with a full temperature sweep, viscosity decreased monotonically between 80 and 130 C. The absolute viscosity level, however, depended strongly on experimental realization. The three recorded E2 runs (GJJ, ZYX, and CHH) gave values of 9462, 18780, and 27350 at 80 C and 1955, 4017, and 6977 at 120 C. The corresponding max/min spreads were 2.89-fold and 3.57-fold. A one-day retest also shifted the measured level for the available repeated samples.

These observations do not mean that the workflow unexpectedly discovered that preparation history exists. Rather, they establish that **preparation/history uncertainty is large enough in this system to affect formulation-level decisions**. A useful design therefore has to distinguish nominal target matching from robustness to the process-state block `z_proc`.

### Thermal holding quantifies a process-state coordinate that can change the formulation decision

The effect of time at temperature became explicit when samples were held at 120 C. E1 increased from 708.7 at 15 min to 776.1 at 60 min and 828.1 at 90 min, corresponding to increases of 9.51% and 16.85%, respectively. E5 showed a much stronger response, increasing from 2210 at 15 min to 3349 at 60 min and 4267 at 90 min. These changes correspond to 51.54% over 15-60 min and 93.08% over 15-90 min.

The strong E1/E5 difference shows that hold time cannot be treated only as passive metadata. In the design flow it is an explicit process-state coordinate whose effect is formulation dependent.

For a fixed temperature T and interval t0 -> t1, define

```text
SI(T; t0,t1) = [eta(T,t1) - eta(T,t0)] / eta(T,t0).
```

For the matched 120 C, 15-60 min interval, SI = 0.0951 for E1 and 0.5154 for E5. The descriptor is introduced for the next design iteration rather than used retroactively to alter the frozen PUR-FRONTIER benchmark.

The corresponding design state becomes at least

```text
s = (x_chem, reaction_history, hold_time, preparation_perturbation).
```

The Agent can evaluate uncertainty or robustness over this state and recommend which states are worth testing, but the transition from a recommended state to an observed viscosity requires laboratory execution by a human operator.

### The Agent recommendation is separated from physical actuation

The main limitation of the Agent is therefore operational, not conceptual: it can evaluate uncertainty and recommend a decision, but it cannot directly impose a synthesis history, set a hot plate, hold a sample for a prescribed time, or read a rheometer by itself.

The paper should make this interface explicit:

```text
computational evidence
-> uncertainty / robustness evaluation
-> Agent recommendation of formulation + measurement point
-> freeze recommendation and adjudication criterion
-> human wet-lab execution
-> physical observation
-> adjudicate Agent recommendation
```

A generic representation of the recommendation layer is

```text
Agent score(s) = target_loss(s) + lambda_U * uncertainty(s) + feasibility_penalties(s),
```

where `s` includes both chemistry and process-state variables. This equation is an architectural description; exact numerical claims must continue to use the corresponding frozen scoring implementation.

The scientific contribution of the Agent is thus **selection under uncertainty**, not autonomous laboratory manipulation.

### Final repeated experiment provides physical adjudication of the recommendation

The follow-up recommendation reduced the PPG2000/PDP-70 reactive fraction and introduced AC1920/TK100. The corrected formulation contained 39.60 parts PPG2000, 39.60 parts PDP-70, 17 parts AC1920, 5 parts TK100, and 20.19 parts MDI according to the supplied laboratory sheet.

The same recommended formulation was then physically measured in two repeat runs. At 120 C, replicate 1 gave 1230, 1189, 1203, and 1228 at 15, 30, 45, and 60 min; replicate 2 gave 1281, 1260, 1289, and 1320. Over the common 15-60 min interval, the two runs changed by -0.16% and +3.04%, respectively. The mean profile changed by only 1.47%. Across the four matched time points, the two-run coefficient of variation ranged from approximately 2.87% to 5.11%.

On the same 15-60 min window, E1 increased by 9.51% and E5 by 51.54%. The final repeated experiment therefore shows that the recommended follow-up point produced a substantially flatter thermal-hold response than the original comparison formulations.

Under the project chronology, the Agent recommendation precedes the final repeated measurement. The final paper should preserve the corresponding timestamped run/commit or immutable recommendation record. With that provenance attached, the final repeat experiment can be described as **prospective physical validation (or prospective physical adjudication) of the Agent recommendation**. The Agent did not perform the experiment; it selected/recommended the point that the human experiment then tested.

This is the preferred closed-loop narrative:

```text
known process-state variables
-> uncertainty-aware formulation model
-> Agent recommends informative/robust point
-> human executes recommended experiment
-> experiment confirms or falsifies recommendation
-> process-state evidence is returned to the design flow
```

This framing is stronger than describing the experiment merely as a post hoc correction, because it tests a pre-measurement recommendation while maintaining the true human-in-the-loop execution boundary.

### Experimental evidence upgrades the next design objective

The experiment supports moving from a purely static viscosity objective to a state-aware objective that distinguishes viscosity magnitude, temperature dependence, hold stability, and uncertainty arising from preparation/history.

A generic next-generation objective can therefore be written as

```text
J_next =
    w_eta L_eta
  + w_T L_temperature
  + w_S L_stability
  + lambda_U U(x_chem, z_proc)
  + penalties(feasibility).
```

Here, `U(x_chem, z_proc)` is not a claim that all process variation is reducible to one scalar. It denotes the uncertainty/robustness term through which the Agent accounts for reaction history, hold-time state, and preparation perturbation when comparing recommendations.

The present data do not justify a universal numerical stability threshold for all polyurethane systems. They do establish that a recommendation judged only by a single fixed-condition viscosity omits a process-relevant dimension that can be measured and explicitly incorporated.

This update does not invalidate the frozen PUR-FRONTIER benchmark. PUR-FRONTIER remains a deterministic benchmark under a fixed historical objective. The experimental recommendation layer is the application layer that asks whether an uncertainty-aware decision transfers to real synthesis and rheology.

### Experimental recommendation Agent and PUR-RECOVER remain different tasks

Two Agent roles must not be conflated.

1. **Experimental recommendation Agent:** uses admissible pre-result evidence and uncertainty information to recommend formulation/measurement points; human operators execute them; the final experiment physically adjudicates the recommendation.
2. **PUR-RECOVER benchmark Agent:** receives a blind bundle and is evaluated on recovery, challenge, and certification of an already frozen deterministic decision chain. Wet-lab results remain excluded from its primary input.

The first role establishes practical scientific usefulness. The second measures reproducibility and auditability of the decision process. Keeping the two roles separate avoids circular validation: experimental success does not define the benchmark gold, and benchmark performance does not manufacture the wet-lab result.

### Mechanistic interpretation and claim boundary

The observed stabilization is consistent with the working hypothesis that partially replacing the original fully reactive resin/polyol fraction reduces the effective concentration of reaction-capable components and thereby suppresses viscosity build-up during thermal holding. However, the present data directly establish rheological stabilization, not a molecular kinetic mechanism. No direct conversion measurement, NCO-consumption kinetics, or spectroscopic time series was collected in the supplied experiment. The manuscript should therefore use wording such as **"consistent with reduced effective reactive fraction"** rather than asserting that a specific chemical pathway has been proven.

## Figure priority for the revised paper

The wet-lab/Agent interface should move ahead of the current computational frontier figures.

- **Figure 1:** human-in-the-loop architecture with a visible digital/physical boundary: chemistry + process-state evidence -> Agent uncertainty evaluation -> recommended points -> human execution -> physical adjudication -> evidence update.
- **Figure 2:** measured 80-130 C viscosity sweeps, emphasizing monotonic temperature response and E2 run-to-run spread as preparation/history sensitivity.
- **Figure 3:** 120 C hold-stability curves for E1 and E5 together with both corrected-formulation replicates; use the shared 15-60 min window for quantitative comparison and show the 90-min E1/E5 points without implying corrected-formulation measurements at 90 min.
- **Figure 4:** recommendation-to-validation panel: process-state coordinates, uncertainty-aware recommendation, observed SI for original and final repeated runs, and the transition from static target matching to state-aware design.
- Later figures: source-grounded rheology, deterministic frontier/backward design, then the independent blinded PUR-RECOVER benchmark.

## Claim summary

**Directly supported by the supplied experimental sheet:**

- strong monotonic temperature dependence in each recorded 80-130 C sweep;
- large run-to-run/process sensitivity in the original E2 formulation;
- strong 120 C viscosity build-up in E1 and especially E5;
- near-flat 15-60 min viscosity response in two repeat runs of the corrected formulation;
- reproducibility of the corrected time profile at the level reported above.

**Supported as an Agent-validation claim when pre-result provenance is attached:**

- the tested follow-up formulation/measurement point was recommended before the final repeated measurement;
- the final repeated experiment therefore prospectively adjudicates the recommendation and supports it within the measured 120 C, 15-60 min domain.

**Interpretive, not directly mechanistically proven:**

- the original stability response originates specifically from the 100% reactive soft-chain polyol/resin fraction;
- AC1920/TK100 suppress build-up specifically by lowering reaction kinetics rather than through another rheological or phase effect.

The manuscript should therefore emphasize an **Agent recommendation -> human execution -> physical validation** result, while preserving the distinction between observed rheology, decision uncertainty, and proposed molecular mechanism.
