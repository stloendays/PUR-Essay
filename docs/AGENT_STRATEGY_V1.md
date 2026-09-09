# PUR-RECOVER V1 Agent strategy

## Design principle

The Agent is a **blinded scientific decision-recovery system**, not an optimizer that owns the answer. The deterministic science layer freezes the rules and gold decision first; the Agent is evaluated afterwards.

## Strategy stack

1. **Closed-book answer withholding** — candidate IDs/material names are anonymized and gold/rank/score fields are removed.
2. **Deterministic tool grounding** — arithmetic, ranking, feasibility, backward threshold solving and local sweeps are Python tools, not LLM mental math.
3. **Complete-decision recovery** — winner guessing alone is insufficient. The run must recover property winner, constrained winner, robust winner or a justified abstention, active constraint, backward threshold, reachability and local trend directions.
4. **Robustness abstention** — if PUR-FRONTIER has not frozen a robust score, `rank_robust` fails deterministically and the Agent must abstain rather than create a convenient heuristic.
5. **Backward design** — solve the continuous NCO:OH threshold needed to cross the MDI-fraction boundary and project to the discrete formulation grid.
6. **Anonymous primary benchmark** — deterministic candidate/material mappings are stored evaluator-side only. Named chemistry can be a secondary benchmark.
7. **Leakage testing** — blind bundles are scanned for gold fields, source candidate IDs and original material names.
8. **Trace gating** — the strategy layer records required tool families. A final response is automatically rejected if the deterministic decision chain is incomplete.
9. **Independent evaluation** — `complete_decision_recovery` is the primary metric; component metrics remain available for diagnosis.
10. **Wet-lab separation** — future prospective measurements are excluded from the primary blind benchmark.

## Versioning choice

`configs/oracle_v2.json` is not rewritten. `PUR-RECOVER V1` uses a separate config. Nominal complete-data feasibility uses point responses plus chemistry/process constraints; uncertainty is reserved for the separately frozen robust decision layer. This prevents legacy uncertainty certification from being silently conflated with the complete-data oracle.

## API secrets

Only environment variables are used:

```bash
export OPENAI_API_KEY='...'
export OPENAI_BASE_URL='...'   # optional
export OPENAI_MODEL='...'
```

Real keys must never be committed.
