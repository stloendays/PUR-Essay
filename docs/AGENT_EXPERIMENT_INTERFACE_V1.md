# Agent–experiment interface V1 — uncertainty-aware recommendation, human actuation

**Status:** current paper-facing design for connecting the scientific Agent to the executed wet-lab study without claiming autonomous laboratory control.

## 1. Core role separation

The Agent is a **decision and recommendation layer**, not a physical actuator.

It can:

- quantify uncertainty around candidate formulations and process states;
- compare nominal versus robust decisions;
- identify points at which uncertainty, process sensitivity, or decision boundaries are most informative;
- recommend formulations, hold conditions, and repeat measurements;
- state a pre-result expected direction/ordering and a falsification criterion;
- issue an auditable recommendation record before the corresponding measurement.

It cannot:

- weigh raw materials;
- control the reactor, heater, rheometer, or sample preparation;
- impose a hold time physically;
- execute a synthesis or measurement by itself.

The human wet-lab operator is therefore the actuator. The scientific claim is **Agent-guided experimental design with human execution**, not autonomous experimentation.

## 2. State representation

The next design flow must distinguish formulation variables from process-state variables.

Let

```text
x_chem = formulation variables
z_proc = process-state variables
```

with the currently identified process-state block

```text
z_proc = {
  reaction_history,
  thermal_hold_time,
  preparation_perturbation
}
```

and rheological response

```text
y = rheology(x_chem, z_proc).
```

Reaction history, thermal hold time, and preparation perturbation are **not treated as newly discovered unknown physics**. They are known scientifically relevant factors that the original static formulation objective did not yet operationalize as explicit design coordinates. The wet-lab study quantifies how strongly these factors matter in the present system and provides the measurements needed to move them into the next design iteration.

## 3. What the Agent actually optimizes

The Agent does not need physical control to make a testable scientific contribution. Its decision problem is to recommend a point or condition whose expected performance remains acceptable under uncertainty, or whose measurement is maximally diagnostic of a decision boundary.

A generic paper-facing representation is

```text
state s = (x_chem, z_proc)

Agent score(s) = target_loss(s) + lambda_U * uncertainty(s) + feasibility_penalties(s)
```

or, for an explicitly diagnostic experiment,

```text
recommended point = argmax_s expected decision value / uncertainty resolution.
```

These expressions describe the architecture rather than replacing the frozen PUR-FRONTIER equations. Exact numerical scoring must come from the corresponding frozen implementation or recommendation trace.

The Agent's output is therefore a **recommendation with uncertainty**, not a motor command.

## 4. Recommendation–execution–adjudication loop

The operational loop is

```text
source evidence + frozen computational state
-> represent chemistry + process-state uncertainty
-> Agent evaluates uncertainty / decision sensitivity
-> Agent recommends formulation + measurement point(s)
-> freeze recommendation and falsification criterion
-> human operator executes the experiment
-> instrument records rheology
-> compare observation with the frozen recommendation
-> supported / partially supported / falsified / out-of-domain
-> update the next design iteration
```

This separation is important. A successful final experiment validates the **quality of the Agent's recommendation**, not an ability to physically perform chemistry.

## 5. Interpretation of the current wet-lab sequence

The current experimental narrative should be written in two levels.

### Level A — transfer and process-state characterization

The initial local formulation matrix tests whether the computationally selected region transfers into the physical laboratory system while explicitly exposing sensitivity to reaction history, hold time, and preparation realization.

Large run-to-run changes and the 120 C hold response are therefore interpreted as measurements of process-state sensitivity, not as a surprise that these variables exist.

### Level B — Agent recommendation and final physical adjudication

Once the relevant uncertainty/process-sensitivity information is available, the Agent recommends the follow-up formulation/measurement point(s) under the available evidence. The wet-lab operator then executes those recommendations.

For the corrected formulation, the two repeated 120 C measurements provide the physical adjudication step: the 15-60 min drifts of -0.16% and +3.04% are substantially flatter than the matched original E1 (+9.51%) and E5 (+51.54%) responses.

The manuscript may describe this final experiment as **prospective physical validation of an Agent recommendation only if the recommendation/point selection can be shown to have been frozen before those final measurements were inspected**. The final paper should attach the corresponding timestamped run, commit, or immutable recommendation record. This protects the chronology without weakening the result.

## 6. Do not conflate two Agent roles

The repository contains two distinct Agent-facing scientific tasks and they should remain separated.

### A. Experimental recommendation Agent

Purpose:

```text
uncertainty-aware recommendation -> human wet-lab execution -> physical adjudication
```

This is the Agent application that connects to the final experiment.

### B. PUR-RECOVER benchmark Agent

Purpose:

```text
blind bundle -> recover frozen deterministic decision chain -> challenge -> certify -> explain
```

PUR-RECOVER remains a benchmark of decision recovery and auditability. It should not be retroactively described as the physical actuator or as the source of wet-lab measurements. Wet-lab data remain excluded from its primary blind input.

The paper can therefore make both claims without leakage:

1. an uncertainty-aware Agent can recommend experimentally useful points while leaving physical execution to a human operator;
2. a separate blinded PUR-RECOVER benchmark tests whether the deterministic scientific decision chain can be recovered reproducibly.

## 7. Paper-facing terminology

Prefer:

- **Agent-guided wet-lab validation**;
- **human-in-the-loop experimental execution**;
- **uncertainty-aware experimental recommendation**;
- **prospective physical adjudication of an Agent recommendation**;
- **process-state variables** for reaction history, hold time, and preparation perturbation.

Avoid:

- **autonomous laboratory**;
- **Agent performed the experiment**;
- **Agent directly controlled the chemistry**;
- describing known process variables as if their existence were discovered for the first time.

## 8. Minimum provenance required for the final Agent-validation claim

For every point claimed as Agent-recommended before experiment, preserve:

```text
recommendation_id
candidate/formulation identity
recommended measurement condition
uncertainty or decision rationale
expected direction / acceptance criterion
git commit or immutable run identifier
generation timestamp
result_inspection_status
human execution timestamp / batch identifier
post-result adjudication
```

A recommendation generated after a result was inspected can still be reported as a closed-loop decision, but it must not be relabelled as prospective for that already-observed result.
