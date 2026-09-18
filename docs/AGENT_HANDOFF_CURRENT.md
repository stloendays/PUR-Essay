# Current Agent handoff — experimental recommender + PUR-RECOVER audit

**Status (2026-09-17):** the project now distinguishes two Agent roles that share scientific infrastructure but answer different questions. Do not merge their data paths or claims.

## 1. Two Agent roles

### A. Experimental recommendation Agent

Purpose:

```text
chemistry + process-state evidence
-> uncertainty / robustness evaluation
-> recommend formulation and measurement point(s)
-> freeze recommendation
-> human wet-lab execution
-> physical adjudication
```

The Agent is a recommender, not an actuator. It may quantify uncertainty, compare robust alternatives, and recommend what should be tested. It does not weigh materials, control synthesis, impose a hold time, or operate the rheometer.

The current process-state block to be carried into the design flow is

```text
z_proc = {
  reaction_history,
  thermal_hold_time,
  preparation_perturbation
}
```

These are known process-relevant variables. The experiment quantifies their practical impact and turns them into explicit design/uncertainty coordinates; it does not claim to discover their existence.

Paper-facing interface specification:

- `docs/AGENT_EXPERIMENT_INTERFACE_V1.md`
- `configs/agent_experiment_recommendation_v1.schema.json`
- `docs/VALIDATION_EXPERIMENT_V8_AGENT_GUIDED.md`

A wet-lab point may be described as prospective validation of an Agent recommendation only when an immutable recommendation record predates inspection of that point's result.

### B. PUR-RECOVER benchmark Agent

Purpose:

```text
real/source-grounded rheology
-> deterministic PUR-FRONTIER V1
-> freeze gold
-> build anonymised blind bundle
-> PUR-RECOVER Agent / baselines / ablations
-> evaluator-only comparison with frozen gold
```

PUR-RECOVER does **not** own the experimental recommendation claim. It is the independent benchmark for reproducible recovery, challenge, certification, and explanation of an already-frozen deterministic decision chain.

Wet-lab measurements remain excluded from the primary PUR-RECOVER benchmark input.

## 2. PUR-RECOVER current status

V2 orchestration is implemented. The real-API V2 pilot ran 24 runs across 8 conditions with no transport errors or invalid outputs; outputs are preserved under `results/recover_v2/pilot_v2_20260911/`.

The pilot's honest reading remains unchanged: the canonical ontology fixed a real interface failure mode, while the additional V2 gates did not yet show measurable advantage at n=3 because all V2 gates passed on the first answer. Do not retune the benchmark to manufacture a positive Agent result.

The V2 orchestration remains:

```text
PLAN -> SOLVE -> CHALLENGE -> CERTIFY -> EXPLAIN
```

## 3. Frozen PUR-RECOVER scientific contract

The evaluator-side deterministic decision chain remains:

```text
L0 property winner      WO_INV_0419
L1 constrained winner   WO_INV_0579
L2 robust winner        WO_INV_0420
active boundary         MDI fraction >= 0.35
continuous threshold    NCO:OH = 1.7719836724
first reachable grid    NCO:OH = 1.8
```

Do not change:

- `PUR_SIM_V1` candidate responses;
- `configs/frontier_v1.json` objective or constraints;
- L0/L1/L2 semantics;
- robust uncertainty propagation;
- backward threshold definition;
- evaluator tolerances to rescue a model;
- blind-bundle anonymisation;
- gold separation.

The 928-candidate benchmark remains an algorithmic/decision benchmark, not empirical rheology evidence.

## 4. Primary PUR-RECOVER task

A complete successful run must recover, in anonymised candidate labels:

1. L0 property winner;
2. L1 nominal constrained winner;
3. L2 robust winner;
4. active constraint;
5. continuous backward threshold;
6. nearest reachable grid point and reachability verdict;
7. local NCO direction;
8. local composition direction.

A lucky Top-1 guess is not complete success. The primary metric remains `complete_decision_recovery`.

## 5. Experimental application contract

The experimental recommendation path is allowed to use process-state uncertainty and recommend measurements, but it must preserve a recommendation/execution boundary.

Minimum record for any paper-facing recommended point:

```text
recommendation_id
candidate/formulation identity
recommended condition
uncertainty / decision rationale
expected direction or acceptance criterion
generation timestamp
git commit or immutable run ID
result_inspection_status
human execution reference
post-result adjudication
```

Use `configs/agent_experiment_recommendation_v1.schema.json` for new records.

The physical experiment may return one of:

```text
supported
partially_supported
falsified
out_of_domain
```

A falsified recommendation is still scientifically useful and must not be rewritten after the fact.

## 6. Current wet-lab interpretation

The original PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI local design provides process-state characterization and physical transfer evidence.

Key observations already recorded:

- E2 max/min spread: approximately 2.89x at 80 C and 3.57x at 120 C;
- E1 120 C drift over 15-60 min: +9.51%;
- E5 120 C drift over 15-60 min: +51.54%;
- follow-up formulation repeat 1: -0.16% over 15-60 min;
- follow-up formulation repeat 2: +3.04% over 15-60 min;
- follow-up mean profile: approximately +1.47%;
- pointwise two-run CV: approximately 2.87-5.11%.

The preferred paper narrative is:

> the Agent evaluates uncertainty and recommends a point; the human laboratory executes the recommendation; the final repeated experiment physically adjudicates the recommendation.

Do not say that the Agent directly operated the lab.

## 7. Historical code and provenance

`src/pur_bridge/agent.py` remains historical provenance for an earlier experiment-selection / information-gain pathway. It should not be silently renamed as PUR-RECOVER.

The current paper may use an experimental recommendation layer, but it must be versioned explicitly and kept conceptually separate from the blind PUR-RECOVER benchmark.

The existing `configs/prospective_adjudication_schema.json` also remains historical for the earlier design in which the running experiment was not changed by the Agent. New uncertainty-aware recommendation records use the separately versioned `configs/agent_experiment_recommendation_v1.schema.json`.

## 8. Canonical PUR-RECOVER code

Use:

- `src/pur_agent/`
- `src/pur_science/`
- `configs/frontier_v1.json`
- `configs/recover_v1.json`
- `configs/recover_v2.json`
- `docs/AGENT_STRATEGY_V1.md`
- `docs/AGENT_WORKFLOW_V2.md`
- `docs/FRONTIER_V1.md`
- `docs/FRONTIER_DEPTH_V1.md`
- `prompts/recover_v1_system.txt`
- `prompts/recover_v1_task.txt`
- `prompts/recover_v2_system.txt`
- `prompts/recover_v2_task.txt`
- `scripts/run_agent_once.py`
- `scripts/run_agent_benchmark.py`
- `scripts/evaluate_agent_runs.py`
- `scripts/verify_no_leakage.py`

## 9. Benchmark conditions to preserve

Existing evidence remains immutable:

```text
oracle
direct_llm
tool_llm
pur_agent
pur_agent_no_backward
pur_agent_no_constraint_checker
pur_agent_no_provenance
pur_agent_single_pass
```

V2 conditions remain separately versioned:

```text
pur_agent_v2
pur_agent_v2_no_evidence_planner
pur_agent_v2_no_challenge
pur_agent_v2_no_cross_path
pur_agent_v2_no_certificate
```

Do not overwrite old pilot records to fit the new experimental framing.

## 10. Secret handling

Never commit a real API credential. Use environment variables only:

```text
OPENAI_API_KEY
OPENAI_BASE_URL
OPENAI_MODEL
OPENAI_PROVIDER
```

## 11. Immediate next steps

1. Recover and attach the immutable pre-result Agent recommendation record for the final wet-lab point so the prospective-adjudication claim has auditable chronology.
2. Keep reaction history, thermal hold time, and preparation perturbation as explicit process-state variables in the next design layer.
3. Build the revised experiment/Agent figures from the existing wet-lab measurements; no additional wet-lab experiment is required by the current manuscript plan.
4. Keep the PUR-RECOVER formal benchmark independent of wet-lab data and report the formal matrix without retuning after results.
5. Assemble manuscript v0.4 around the recommendation -> human execution -> physical validation architecture.
