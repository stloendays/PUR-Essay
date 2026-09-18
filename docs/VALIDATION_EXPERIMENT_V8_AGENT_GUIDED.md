# Wet-lab validation V8 — Agent-guided recommendation with human execution

**Status:** current interpretation of the laboratory study. V6 remains the pre-result instrument-aware plan; V7 records the earlier experiment-first interpretation. V8 refines the scientific role of the Agent and the process-state variables without changing any measured value.

## 1. Central design

The experiment is not an autonomous-lab demonstration. It is a **human-in-the-loop validation of an uncertainty-aware Agent recommendation**.

```text
chemistry/formulation state
+ process-state variables
+ uncertainty model
        |
        v
Agent recommends formulation / measurement point
        |
        v
recommendation is frozen
        |
        v
human operator synthesizes and measures
        |
        v
physical result adjudicates the recommendation
```

The Agent may quantify uncertainty, compare robust alternatives, and recommend what should be tested. It does not physically manipulate the formulation or instrument.

## 2. Process-state variables are part of the design flow

The process-state block is explicitly

```text
z_proc = {
  reaction_history,
  thermal_hold_time,
  preparation_perturbation
}
```

These factors are known to matter in reactive rheology. The current experiment does not claim to discover their existence. Instead, it measures their magnitude and formulation dependence sufficiently to justify moving them from informal laboratory context into explicit design variables/uncertainty dimensions.

This means that the E2 run-to-run spread and the 120 C hold curves should be interpreted as **process-state sensitivity measurements**, not merely as failed reproducibility.

## 3. Executed local design

| ID | PPG2000/PDP-70 | NCO:OH | PPG2000 | PDP-70 | MDI |
|---|---:|---:|---:|---:|---:|
| E1 | 50/50 | 1.70 | 121.07 | 121.07 | 57.86 |
| E2 | 50/50 | 1.80 | 119.71 | 119.71 | 60.57 |
| E3 | 50/50 | 1.90 | 118.39 | 118.39 | 63.23 |
| E4 | 60/40 | 1.80 | 144.30 | 96.20 | 59.50 |
| E5 | 40/60 | 1.80 | 95.35 | 143.02 | 61.63 |

The source sheet reports these amounts in grams for E1-E5.

## 4. Process-history/preparation sensitivity

The available 80-130 C sweeps decrease monotonically with temperature but show large absolute run-to-run spread in the original system. E2 spans 9462-27350 at 80 C and 1955-6977 at 120 C across the GJJ/ZYX/CHH runs, corresponding to max/min spreads of approximately 2.89x and 3.57x.

The correct inference is not that preparation history was previously unknown. It is that preparation/history sensitivity is large enough to affect the reliability of a formulation decision and therefore belongs in the uncertainty-aware recommendation layer.

## 5. Hold time as an explicit process coordinate

At 120 C:

| Formulation | eta15 | eta60 | eta90 | 15->60 | 15->90 |
|---|---:|---:|---:|---:|---:|
| E1 | 708.7 | 776.1 | 828.1 | +9.51% | +16.85% |
| E5 | 2210 | 3349 | 4267 | +51.54% | +93.08% |

Define

```text
SI(T; t0,t1) = [eta(T,t1) - eta(T,t0)] / eta(T,t0).
```

For the shared 120 C, 15-60 min window:

```text
E1: SI = 0.0951
E5: SI = 0.5154
```

The large difference demonstrates a formulation-dependent response to a process-state coordinate. A future Agent recommendation should therefore evaluate a state `(x_chem, z_proc)`, not composition alone.

## 6. Agent recommendation and final physical adjudication

The follow-up formulation contains:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

The source sheet reports these as parts and does not explicitly report NCO:OH; no NCO:OH value is inferred.

Two repeat runs of the same formulation were measured at 120 C:

| time | repeat 1 | repeat 2 | mean | two-run CV |
|---:|---:|---:|---:|---:|
| 15 min | 1230 | 1281 | 1255.5 | 2.87% |
| 30 min | 1189 | 1260 | 1224.5 | 4.10% |
| 45 min | 1203 | 1289 | 1246.0 | 4.88% |
| 60 min | 1228 | 1320 | 1274.0 | 5.11% |

The 15->60 min drifts are:

```text
repeat 1: -0.16%
repeat 2: +3.04%
mean profile: +1.47%
```

These final measurements are substantially flatter than E1 (+9.51%) and E5 (+51.54%) over the same 15-60 min interval.

The paper-facing interpretation is therefore:

> The Agent evaluated the available design uncertainty and recommended the follow-up point; the human operator executed the recommended formulation and measurement; the repeated experiment then physically adjudicated the recommendation and showed a stable 120 C hold response within the measured window.

For this sentence to be labelled **prospective**, the repository must preserve an immutable Agent recommendation record that predates inspection of the final repeat results. The measured values themselves are not altered by this provenance requirement.

## 7. Next design objective

The next formulation state should include

```text
s = (x_chem, reaction_history, thermal_hold_time, preparation_perturbation)
```

and a state-aware objective may be represented generically as

```text
J_next =
    w_eta L_eta
  + w_T L_temperature
  + w_S L_stability
  + lambda_U U(s)
  + feasibility_penalties.
```

The Agent is responsible for evaluating/ranking under uncertainty. Human operators remain responsible for changing the physical state and producing measurements.

## 8. Two Agent roles remain separated

### Experimental recommendation Agent

```text
uncertainty-aware recommendation
-> human execution
-> physical adjudication
```

### PUR-RECOVER benchmark Agent

```text
blind deterministic task
-> recover decision chain
-> challenge
-> certify
-> explain
```

Wet-lab results remain excluded from the primary PUR-RECOVER input. The recommendation task demonstrates application value; PUR-RECOVER separately tests reproducibility and auditability.

## 9. Current manuscript consequence

The paper should no longer use the phrase "the experiment discovered an unknown hidden variable" for reaction history, hold time, or preparation perturbation. Instead:

- these variables are known and are being formalized in the design state;
- the experiment quantifies their practical impact;
- the Agent uses uncertainty over this augmented state to recommend what should be tested;
- the human laboratory executes the recommendation;
- the final repeated experiment provides the physical validation.

No additional wet-lab experiment is required by this framing. The remaining work is provenance freezing, analysis, figure production, and manuscript integration.
