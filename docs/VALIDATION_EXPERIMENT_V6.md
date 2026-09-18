# Prospective wet-lab validation V6 — instrument-aware common-material plan

**Status:** historical pre-result execution plan. Retained for provenance. The experiment has since been executed; use `VALIDATION_EXPERIMENT_V8_AGENT_GUIDED.md` for the current paper-facing interpretation.

V6 added an explicit instrument-window feasibility gate after laboratory feedback that the pre-MDI PPG2000/PDP-70 system could fall below the lower useful range of the available viscometer. It did not yet formalize the current Agent-recommendation / human-actuation boundary.

## 1. Frozen chemistry

Reactive system:

```text
PPG2000 + STEPANPOL PDP-70 + 4,4'-MDI
```

Five formulations:

| Role | PPG2000 / PDP-70 (polyol wt parts) | NCO:OH | Main question |
|---|---:|---:|---|
| N- | 50 / 50 | 1.70 | lower-stoichiometry response |
| CTR | 50 / 50 | 1.80 | centre/reference |
| N+ | 50 / 50 | 1.90 | higher-stoichiometry response |
| C-P | 60 / 40 | 1.80 | PPG2000-rich response |
| C-E | 40 / 60 | 1.80 | PDP-70-rich response |

Original replication plan:

```text
5 formulations x 3 independent synthesis batches = 15 independent syntheses
```

No third polyol or other raw material was to be added merely to make a viscosity instrument return a value, because that would change the formulation identity and hypothesis.

## 2. Measurement-feasibility gate

Before assigning a temperature point to a formal rheology dataset, verify that the expected or observed viscosity is inside the calibrated range of the selected instrument/geometry.

Required metadata:

- instrument model;
- spindle/geometry;
- rotational speed or shear condition;
- lower reliable torque/viscosity limit;
- sample volume;
- sample temperature;
- conditioning history.

Decision rule:

```text
inside calibrated range -> report quantitative viscosity
below lower range -> report left-censored / below-range status
above upper range -> report right-censored / above-range status
```

Never encode below-range as zero and never silently drop it as ordinary missing data.

## 3. Pre-MDI plan

The earlier unconditional requirement to measure the pre-MDI blend directly at 80/90/100/110/120 C was removed.

If the blend was below the useful range of the available viscometer, the plan required either a lower-viscosity-capable geometry/method or an explicit censored feasibility observation rather than an invented value.

## 4. Post-MDI plan

The NCO-terminated prepolymer remained the primary process-relevant rheology target.

Candidate temperature window:

```text
80 / 90 / 100 / 110 / 120 C
```

with an instrument-window gate at every point.

## 5. Historical workflow implication

V6 separated chemical/process feasibility from instrument feasibility:

```text
candidate generation
-> chemistry/process feasibility
-> instrument-window feasibility
-> wet-lab execution
-> evidence update
```

V8 extends this architecture by making reaction history, thermal hold time, and preparation perturbation explicit process-state variables and by inserting an uncertainty-aware Agent recommendation step before human wet-lab actuation.

No values in V6 are the current experimental results; use the structured files under `data/prospective_validation/` and V8 for executed-result interpretation.
