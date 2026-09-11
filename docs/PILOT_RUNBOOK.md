# PUR-RECOVER V1 real-API pilot runbook

Pilot = 5 runs each of `direct_llm`, `tool_llm`, `pur_agent`. It is a stability check of the
transport, schema and tool plumbing. Pilot numbers are not manuscript results and are never
used to tune prompts, tolerances or conditions. Every run, including failures, invalid JSON
and timeouts, is kept.

## 0. Preconditions (all verified 2026-09-10)

```text
pytest                       77 passed
freeze_frontier_v1           GOLD, table sha256 d8623116…, expectation_all_agree = true
build_blind_bundle           benchmark/recover_v1/blind, leakage PASS
verify_no_leakage            PASS, 8 guard probes refused
mock smoke                   all 9 conditions run; pur_agent / pur_audit complete under mock
```

## 1. Credentials — environment variables only

No `OPENAI_*` variable exists at process, user or machine scope on this machine, and there is
no `.env`. Set them for the shell session (never commit, never paste into files):

PowerShell:

```powershell
$env:OPENAI_API_KEY  = "<your key>"
$env:OPENAI_BASE_URL = "<https://.../v1 for an OpenAI-compatible endpoint; leave unset for api.openai.com>"
$env:OPENAI_MODEL    = "<model id, e.g. gpt-Luna>"
$env:OPENAI_PROVIDER = "auto"     # auto = Responses API first, Chat Completions fallback; or "chat"
```

bash:

```bash
export OPENAI_API_KEY="..."; export OPENAI_BASE_URL="..."; export OPENAI_MODEL="..."; export OPENAI_PROVIDER=auto
```

## 2. Pilot commands

```bash
python scripts/run_agent_once.py --condition pur_agent --seed 1                       # single connectivity run
python scripts/run_baselines.py --conditions direct_llm tool_llm pur_agent --runs 5 --seed-base 1000 --results-root results/recover_v1/pilot_20260910
python scripts/summarize_benchmark.py results/recover_v1/pilot_20260910
```

Optional secondary mode after the primary pilot is stable:

```bash
python scripts/run_agent_benchmark.py --condition pur_audit --runs 3 --seed-base 2000 --out-dir results/recover_v1/pilot_20260910/pur_audit/<model>
```

## 3. What to look at

- `results/recover_v1/pilot_20260910/summary.csv`: `n_valid_output`, `n_errors`, `complete_decision_recovery_rate`, `tool_call_count_mean`, token means, latency.
- Per-run JSON under `.../runs/`: `error`, `fallback_transport_used` (tells you whether the endpoint served the Responses API), `strategy_check`, `tool_trace`.
- Failure taxonomy: schema/API error → `error`/`invalid_output`; ranking error → winner recovery flags; constraint error → `active_constraint_recovery`; backward error → `backward_threshold_error`; reachability → `reachability_recovery`.

## 4. After the pilot

Freeze prompt/config/data hashes (they are already recorded in each run record), then start the
formal 30–50 run matrix with a declared seed schedule. Do not change any condition after formal
results are visible.

---

# PUR-RECOVER V2 real-API pilot runbook (2026-09-11)

Same discipline as V1: the pilot is a plumbing check, not a result. Do not tune prompts,
tolerances or conditions on what it shows. Keep every failure.

V2 runs against its own bundle, `benchmark/recover_v2/blind`, whose candidate table is
byte-identical to V1's (`6ca33d4e…`) so the two versions are directly comparable. Its gold is
scientifically identical to V1's.

## 0. Preconditions (verified 2026-09-11)

```text
pytest -q                    129 passed
freeze_frontier_v1           GOLD, table sha256 d8623116…, 0419 / 0579 / 0420, 1.771983672436161 -> 1.8, expectation_all_agree = true
build_blind_bundle (V1)      benchmark/recover_v1/blind, leakage PASS, artefacts byte-unchanged
build_blind_bundle (V2)      benchmark/recover_v2/blind, leakage PASS, same candidate hash as V1
verify_no_leakage (V1, V2)   PASS, 8 guard probes refused each
mock smoke (V1)              8 conditions; tool_llm / pur_agent / no_provenance / single_pass complete, ablations degrade as designed
mock smoke (V2)              5 conditions; all complete, certificate_pass 1.0, cross-path difference 0.0
```

**Blocker:** the configured endpoint `http://127.0.0.1:8788/v1` refuses connections. Start it
and confirm it answers before spending any runs.

## 1. Connectivity check

```bash
python scripts/run_agent_once.py --condition pur_agent_v2 --blind-dir benchmark/recover_v2/blind --seed 1
```

Check `error` is null, `fallback_transport_used`, and that `gate_attempts` is non-empty —
an empty `gate_attempts` means the transport never submitted a final answer to the gate.

## 2. Small pilot (3 runs per condition)

```bash
python scripts/run_baselines.py --conditions tool_llm pur_agent pur_agent_v2 --runs 3 --seed-base 3000 --blind-dir benchmark/recover_v2/blind --results-root results/recover_v2/pilot_v2_20260911
```

`tool_llm` and `pur_agent` are re-run here against the V2 bundle so the comparison is
within-bundle. Their V1 pilot records under `results/recover_v1/pilot_20260910_b/` stay
untouched.

Then the ablations, once the full condition is stable:

```bash
python scripts/run_baselines.py --conditions pur_agent_v2_no_evidence_planner pur_agent_v2_no_challenge pur_agent_v2_no_cross_path pur_agent_v2_no_certificate --runs 3 --seed-base 3000 --blind-dir benchmark/recover_v2/blind --results-root results/recover_v2/pilot_v2_20260911
python scripts/summarize_benchmark.py results/recover_v2/pilot_v2_20260911
```

## 3. What to look at

Primary metric is still `complete_decision_recovery_rate`. The V2 question is whether anything
*else* separates `pur_agent_v2` from `tool_llm`:

| column | reads as |
|---|---|
| `scientific_correctness_rate` vs `schema_correctness_rate` | the split the V1 pilot could not make |
| `first_answer_gate_clean_rate`, `gate_retries_mean` | how much of the schema advantage the gate itself produced — report with the schema rate, never instead of it |
| `evidence_coverage_ratio_mean` | claim support, not tool-button coverage |
| `cross_path_agreement_rate`, `cross_path_absolute_difference_mean` | dual-path verification |
| `contradiction_detection_rate` | reported contradictions vs the deterministic count |
| `unnecessary_tool_calls_mean` | off-plan calls plus identical repeats; the required challenge and the Path-B cross-check are excluded |
| `certificate_pass_rate` | the machine trust signal, not `confidence` |
| `abstention_or_conflict_rate` | structured conflict instead of a manufactured answer |
| `api_calls_mean`, `input_tokens_mean`, `output_tokens_mean`, `latency_s_mean`, `cost_usd_mean` | what the contract costs |

`cost_usd_mean` stays null until `evaluation.pricing_usd_per_1k_tokens` is filled in
`configs/recover_v2.json`.

## 4. Freeze before the formal matrix

Commit first — the manifest records worktree cleanliness and refuses to overwrite itself:

```bash
python scripts/freeze_run_manifest.py --label formal_v2_<date> --benchmark recover_v2 --runs 30 --seed-base 5000 --conditions direct_llm tool_llm pur_agent pur_agent_v2 pur_agent_v2_no_evidence_planner pur_agent_v2_no_challenge pur_agent_v2_no_cross_path pur_agent_v2_no_certificate
```

Comparable conditions use the same run count and the same seed schedule. Nothing is changed
after formal results are visible; if a scientific-contract bug is found, version the benchmark
and rerun the affected conditions instead of patching in place.
