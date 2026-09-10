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
