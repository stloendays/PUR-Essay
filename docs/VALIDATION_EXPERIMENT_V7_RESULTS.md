# Wet-lab validation V7 — executed experiment-first result

**Status:** historical interpretation retained for provenance. This version promoted the executed wet-lab study to the main physical result, but it treated the follow-up primarily as a failure-aware closed-loop correction. It is now superseded by `VALIDATION_EXPERIMENT_V8_AGENT_GUIDED.md`, which preserves the same measurements while making the Agent recommendation / human execution boundary explicit and treating reaction history, hold time, and preparation perturbation as known process-state variables entering the design flow.

## 1. Role of the experiment in V7

V7 established two useful distinctions that remain valid:

- the original local design supplies physical transfer and process-state evidence;
- the final follow-up formulation has repeated 120 C measurements and should be compared to the original formulations on the shared 15-60 min window.

V8 refines the causal/decision narrative: the scientific Agent evaluates uncertainty and recommends points, while the human wet-lab operator physically executes them. The final repeated experiment can be used as prospective physical adjudication of an Agent recommendation when the pre-result recommendation provenance is attached.

## 2. Executed local design

| ID | PPG2000/PDP-70 | NCO:OH | PPG2000 | PDP-70 | MDI |
|---|---:|---:|---:|---:|---:|
| E1 | 50/50 | 1.70 | 121.07 | 121.07 | 57.86 |
| E2 | 50/50 | 1.80 | 119.71 | 119.71 | 60.57 |
| E3 | 50/50 | 1.90 | 118.39 | 118.39 | 63.23 |
| E4 | 60/40 | 1.80 | 144.30 | 96.20 | 59.50 |
| E5 | 40/60 | 1.80 | 95.35 | 143.02 | 61.63 |

The source sheet reports these amounts in grams for E1-E5.

## 3. Process-state evidence

The available 80-130 C sweeps show monotonic viscosity decrease with temperature but large absolute run-to-run spread in the original system. E2 spans 9462-27350 at 80 C and 1955-6977 at 120 C across the GJJ/ZYX/CHH runs.

At 120 C:

| Formulation | eta15 | eta60 | eta90 | 15->60 | 15->90 |
|---|---:|---:|---:|---:|---:|
| E1 | 708.7 | 776.1 | 828.1 | +9.51% | +16.85% |
| E5 | 2210 | 3349 | 4267 | +51.54% | +93.08% |

V8 interprets these as explicit measurements of preparation/history and hold-time sensitivity rather than as the discovery of unknown hidden variables.

## 4. Follow-up formulation and repeated measurements

The supplied follow-up formulation is:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

The source sheet labels these as parts and does not explicitly report NCO:OH; no NCO:OH value is inferred.

Two repeat runs at 120 C are:

| time | repeat 1 | repeat 2 | mean | two-run CV |
|---:|---:|---:|---:|---:|
| 15 min | 1230 | 1281 | 1255.5 | 2.87% |
| 30 min | 1189 | 1260 | 1224.5 | 4.10% |
| 45 min | 1203 | 1289 | 1246.0 | 4.88% |
| 60 min | 1228 | 1320 | 1274.0 | 5.11% |

15->60 min drift:

- repeat 1: -0.16%
- repeat 2: +3.04%
- two-repeat mean profile: +1.47%

For the matched 15-60 min window, the original E1 and E5 drifts are +9.51% and +51.54%, respectively.

## 5. Current pointer

Use `VALIDATION_EXPERIMENT_V8_AGENT_GUIDED.md` for current manuscript wording and `AGENT_EXPERIMENT_INTERFACE_V1.md` for the Agent / human-actuation contract.

No measured values were changed by the V7 -> V8 reframing.
