# Model-selection probe — protocol frozen BEFORE the runs (2026-09-11)

## Why

The 2026-09-11 V2 pilot found every tool-using condition at ceiling on `gpt-5.6-luna`
(`tool_llm` 2/3, everything else 3/3, gate retries 0 across all 15 V2 runs). A formal matrix
run against a saturated task mostly buys precision on a ceiling: it cannot show whether the
planning/gating layer does anything, because the gate never fires.

This probe selects a model on which the *task itself* still discriminates.

## Selection rule (declared before any probe run)

The selection is made on **`tool_llm` alone**. No V2 condition is run in this probe, and no V2
result may influence the choice. This is the whole point: choosing a model by looking at how
`pur_agent_v2` performs on it would be selecting the model that flatters the Agent.

1. Run `tool_llm` only, 5 runs, seeds 4001-4005, on each candidate model.
2. Compute `complete_decision_recovery_rate` per model.
3. Choose the model with a rate in the open interval **(0.0, 1.0)** — the task is neither
   saturated nor impossible. If several qualify, take the one closest to **0.6**, which gives
   the most headroom in both directions for a fixed run count.
4. If no model falls in (0.0, 1.0), report that and do not substitute a different criterion.
   In that case the formal matrix stays on `gpt-5.6-luna` and is sized to resolve a low
   failure rate instead, which is the other branch of the decision.

`gpt-5.6-luna` is included as the reference point already measured.

## Candidate models

Served by the local proxy: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, `gpt-5.2`.
Probed here: `gpt-5.2` and `gpt-5.5` (the two plausibly weaker ones).

## What this probe is not

- Not a benchmark result. Five runs of one condition cannot support any claim about models.
- Not a manuscript comparison across models.
- Not a reason to change any prompt, tolerance, condition or gold. Nothing in the frozen
  science or the evaluator may be touched on the basis of what this probe shows.

## Provenance

- git commit at probe time: recorded in each run record (`prompt_sha256`, `config_sha256`,
  `data_sha256`).
- bundle: `benchmark/recover_v2/blind` (candidate table `6ca33d4e…`, identical to V1's).
- All runs kept, including failures.

---

# Probe outcome (recorded after the runs; protocol above is unchanged)

`tool_llm` only, 5 runs, seeds 4001-4005, bundle `benchmark/recover_v2/blind`.

| model | n | transport errors | valid | complete | scientifically correct | canonical spelling |
|---|---|---|---|---|---|---|
| `gpt-5.2` | 5 | **5** | 0 | 0/5 | – | – |
| `gpt-5.5` | 5 | 0 | 5 | **4/5** | 5/5 | 4/5 |
| `gpt-5.6-luna` | 5 | 0 | 5 | **2/5** | 5/5 | 2/5 |

## `gpt-5.2` is excluded on technical grounds, not ability

All five runs returned HTTP 400 from the proxy: *"The 'gpt-5.2' model is not supported when
using Codex with a ChatGPT account."* The model is listed by `/v1/models` but not servable.
Its 0/5 is a transport failure and **must not be read as a task-difficulty measurement**. The
five error records are kept as transport-failure evidence.

## `gpt-5.6-luna` is not at ceiling after all

The 2026-09-11 pilot measured `tool_llm` at 2/3 on three runs. At five runs on different seeds
it is 2/5. The earlier reading of "every tool-using condition at ceiling" was a small-sample
artifact of n=3; the baseline failure rate is closer to 60% than to 0.

## The selection rule ties, and the tie-break is declared here

Rule: pick the qualifying model closest to 0.6. `gpt-5.5` is 0.8 and `gpt-5.6-luna` is 0.4 —
both are 0.2 away. The frozen rule does not break this tie.

Tie-break, chosen without running any V2 condition on `gpt-5.5`: **`gpt-5.6-luna` is the
primary model, `gpt-5.5` the secondary.** The reason is comparability, not performance — every
preserved V1 and V2 record already uses `gpt-5.6-luna`, so keeping it as primary means the
formal matrix can be read against all existing evidence. `gpt-5.5` is retained as a second
model precisely because its baseline sits on the other side of 0.6; two models bracketing the
range test the finding harder than either alone.

## The finding the probe actually produced

Pooling every valid `tool_llm` run recorded so far (pilot seeds 3001-3003 plus probe seeds
4001-4005, both models):

```text
13 valid runs
13/13  scientifically correct
 8/13  canonical spelling
 5/13  failed the primary metric -- ALL FIVE on the constraint name, none on any science
```

The five failures wrote `mdi_fraction_min` (×4, copied from the V1 tool's own
`solve_backward_threshold.constraint` output) and `mdi_fraction_of_polyol_plus_mdi` (×1, copied
from the raw config key). Both are registered aliases resolving to `mdi_fraction`, so both are
scored scientifically correct and non-canonical in spelling.

Across 13 runs and two models there is **not one scientific error** in this baseline. Its
entire primary-metric failure rate is an interface defect — the defect `tool_llm_v2_ontology`
is built to isolate and the V2 toolbox is built to remove.

This changes what the formal matrix is for. See `docs/FORMAL_MATRIX_V2_DESIGN.md`.
