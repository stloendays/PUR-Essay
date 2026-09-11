# Measurement-feasibility gate for PUR wet-lab validation

## Purpose

This gate prevents a chemically valid formulation from being mislabeled as an experimental failure simply because the available instrument cannot resolve its viscosity.

## Rule

Before a viscosity point enters the quantitative experimental dataset, verify that the sample/temperature/method combination lies inside the calibrated range of the selected instrument and geometry.

```text
chemically feasible != automatically measurable
measurability is a property of sample x condition x method
```

## Required metadata

Record instrument model, spindle/geometry, speed or shear condition, lower and upper reliable limits, sample temperature, sample volume, and conditioning history.

## Censoring semantics

- below lower measurement limit -> left-censored / below-range
- above upper measurement limit -> right-censored / above-range
- inside calibrated range -> quantitative value

Do not encode censored observations as zero and do not silently discard them.

## Current PPG2000/PDP-70 implication

Laboratory feedback indicates that the pre-MDI PPG2000/PDP-70 system is too low in viscosity for the currently available viscometer configuration. Because ordinary polyol viscosity decreases as temperature increases, moving directly to 80-120 C on the same setup is not expected to solve the problem.

Preferred responses are, in order:

1. use a lower-viscosity-capable geometry/instrument;
2. use a lower-temperature liquid-state window if scientifically relevant;
3. retain a censored/out-of-range observation if no suitable method is available.

Do not add an extra formulation component solely to bring the sample into the instrument range unless that new chemistry is itself the intended experimental variable.

## Agent integration

Any future wet-lab recommendation should pass:

```text
candidate -> chemistry/process feasibility -> measurement feasibility -> experiment
```

Failure at the measurement-feasibility gate triggers a method adaptation, not automatic rejection of the formulation.
