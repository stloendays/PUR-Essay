# Reproducibility and claim boundaries

This file defines what the paper may and may not claim before prospective E6* data exist.

## Frozen evidence

US5932680A Examples 5–9 are treated as **frozen historical anchor values** for the preregistered decision problem. They are not remeasured and are not assigned artificial replicate precision. The analysis therefore does not claim that the patent point values are noise-free laboratory truth.

The old v0.7 model is also frozen. External-test failures and the 0/928 uncertainty-certified result are retained as evidence motivating abstention and model arbitration; they must not be refit away after observing E6*.

## Prospective evidence

Only E6* and any later Agent-selected transfer experiment are new wet-lab evidence. The primary endpoint is the independent-batch geometric mean of prepolymer viscosity at 130 C. Three independent syntheses are the preregistered minimum.

Technical repeats estimate measurement repeatability but do not substitute for synthesis replication.

## Interpretation tiers

- **ANCHOR_COMPATIBLE**: material chemistry and disclosed property specifications support a patent-anchored prospective counterfactual interpretation.
- **SURROGATE_ONLY**: E6* remains publishable as a modern specification-matched transfer test, but absolute agreement with historical viscosity anchors must not be described as exact replication.
- **INCOMPATIBLE**: the Agent abstains from the historical absolute-viscosity hypothesis test.

Because the exact historical Hercules beta-pinene tackifier grade is not disclosed, even the strongest claim should use "patent-anchored prospective counterfactual" rather than "exact replication" unless stronger documentary evidence is obtained.

## Statistical discipline

1. Report the preregistered 33/40 Pa.s decision zones unchanged.
2. Report the continuous context-transfer coefficient theta regardless of zone classification.
3. Report Bayes-factor sensitivity across the frozen sigma_log grid; do not select sigma after seeing E6*.
4. Use batch-level uncertainty for the primary endpoint. If the 95% batch CI crosses the relevant 33 or 40 Pa.s boundary, the Agent requests replication even when the point estimate is decisive.
5. Treat 110/120/130 C temperature-response analysis as secondary; it cannot replace the 130 C primary endpoint.

## Agent claim

The Agent is an auditable orchestration/decision layer, not a numerical predictor. Numerical predictions, information gain, material gates and statistical decisions are produced by deterministic tools. The LLM may retrieve evidence and explain a decision but cannot alter hard gates or numerical outputs.
