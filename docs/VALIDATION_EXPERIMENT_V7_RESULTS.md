# Wet-lab validation V7 — executed experiment-first result

**Status:** replaces V6 as the current interpretation of the laboratory work. V6 is retained as the pre-result execution plan.

## 1. Role of the experiment

The executed wet-lab study is now the principal physical evidence in the paper rather than a pending secondary check.

Two validation stages must be distinguished:

- **Stage A — prospective external wet-lab validation:** the frozen local E1-E5 design is transferred to laboratory measurements after the computational design has been defined.
- **Stage B — closed-loop follow-up validation:** the initial experiment reveals thermal-hold/process sensitivity; a corrected formulation is then proposed and measured twice. Because the correction uses feedback from Stage A, Stage B is not described as blind external validation.

No further wet-lab experiment is required by the current paper plan.

## 2. Executed local design

| ID | PPG2000/PDP-70 | NCO:OH | PPG2000 | PDP-70 | MDI |
|---|---:|---:|---:|---:|---:|
| E1 | 50/50 | 1.70 | 121.07 | 121.07 | 57.86 |
| E2 | 50/50 | 1.80 | 119.71 | 119.71 | 60.57 |
| E3 | 50/50 | 1.90 | 118.39 | 118.39 | 63.23 |
| E4 | 60/40 | 1.80 | 144.30 | 96.20 | 59.50 |
| E5 | 40/60 | 1.80 | 95.35 | 143.02 | 61.63 |

The source sheet reports these amounts in grams for E1-E5.

## 3. Experimental failure mode

The available 80-130 C sweeps show monotonic viscosity decrease with temperature but large absolute run-to-run spread in the original system. E2, for example, spans 9462-27350 at 80 C and 1955-6977 at 120 C across the GJJ/ZYX/CHH runs.

The 120 C hold experiment identifies the more consequential failure mode:

| Formulation | eta15 | eta60 | eta90 | 15->60 | 15->90 |
|---|---:|---:|---:|---:|---:|
| E1 | 708.7 | 776.1 | 828.1 | +9.51% | +16.85% |
| E5 | 2210 | 3349 | 4267 | +51.54% | +93.08% |

Thus, formulation selection based only on a static viscosity target does not capture thermal-hold stability.

## 4. Closed-loop correction and repeated confirmation

The supplied corrected formulation is:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

The source sheet labels these as parts. It does not explicitly report NCO:OH for this corrected row, so no NCO:OH value is inferred.

Two repeat runs of the same corrected formulation were measured at 120 C:

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

For the matched 15-60 min window, the original E1 and E5 drifts are +9.51% and +51.54%, respectively. The corrected formulation therefore shows a substantially flatter time response in both repeated runs.

## 5. Revised scientific conclusion

The central experimental conclusion is:

> A static viscosity-targeting formulation workflow can transfer to the laboratory yet fail on process-time stability. Prospective wet-lab testing exposed a strong formulation-dependent viscosity build-up at 120 C. A failure-aware formulation correction that reduced the original reactive fraction and introduced AC1920/TK100 was followed by two repeated measurements with near-flat 15-60 min viscosity response. The experiment therefore converts a one-shot inverse-design workflow into a closed-loop, stability-aware formulation workflow.

The data establish rheological stabilization. The proposed reduction in effective reactive fraction is retained as a mechanistic rationale, not claimed as direct kinetic proof.

## 6. Workflow update

```text
source evidence / database
-> frozen local inverse-design decision
-> prospective wet-lab validation
-> quantify temperature response + process sensitivity
-> identify hold-stability failure
-> correction proposal
-> repeated wet-lab confirmation
-> add hold-stability term to next design objective
```

The blind Agent recovery benchmark remains isolated from these experimental records.

## 7. Manuscript consequence

The wet-lab results move to the front of Results and Discussion. Public-source rheology and deterministic FRONTIER analyses become mechanistic/contextual support; the Agent benchmark becomes the methodological audit layer. Figure numbering should be revised accordingly during v0.4 assembly.