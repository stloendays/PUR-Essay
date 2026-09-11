# PUR-RECOVER V2 formal matrix — design

**Status:** design, frozen before execution. Written 2026-09-11 after the V2 pilot
(`results/recover_v2/pilot_v2_20260911/`) and the model probe
(`results/recover_v2/model_probe_20260911/`).

## 1. What the earlier plan got wrong

The plan inherited from `docs/AGENT_WORKFLOW_V2.md` §12 was "30-50 runs of eight conditions".
Two findings make that the wrong matrix.

**The baseline is not at ceiling.** The pilot's `tool_llm` 2/3 looked like saturation at n=3.
At n=5 on fresh seeds it is 2/5 on `gpt-5.6-luna` and 4/5 on `gpt-5.5`. There is plenty of
headroom; the problem was sample size, not difficulty.

**The baseline makes exactly one kind of mistake.** Pooling all 13 valid `tool_llm` runs
across both models and both seed sets:

```text
13/13  scientifically correct
 8/13  canonical spelling
 5/13  failed the primary metric -- all five on the constraint name, none on any science
```

Four failures wrote `mdi_fraction_min`, copied from the V1 tool's own
`solve_backward_threshold.constraint` field; one wrote `mdi_fraction_of_polyol_plus_mdi`,
copied from the raw config key. Not one run got a winner, a threshold, a grid point, a
reachability verdict or a trend wrong.

So the interesting question is no longer "can an Agent recover the chain". With deterministic
tools, this model already does, every time. The question is **which part of the V2 contract
removes the remaining failure mode**, and the answer is testable with far fewer runs than 50.

## 2. What the matrix must resolve

**Q1 (primary). Does the canonical ontology remove the failure mode?**
Paired comparison of `tool_llm` against `tool_llm_v2_ontology`. These differ in exactly one
thing — the vocabulary the tools speak — and are matched on prompt, tool policy, gating (none),
output schema and seed. This is the question the pilot could not answer, because every V2
condition changed prompt, tools and gate at once.

**Q2 (secondary). Does the planning/gating layer add anything beyond the ontology?**
`tool_llm_v2_ontology` against `pur_agent_v2`. If the ontology alone closes the gap, the honest
conclusion is that the gates are not carrying the result, and §13 of the workflow doc applies.

**Q3 (tertiary). Which gate, if any, binds?**
The four V2 ablations. In the pilot `gate_retries = 0` in all 15 V2 runs, so nothing bound.
With the baseline failure rate now known to be ~60% on `gpt-5.6-luna`, this is worth one more
look, but it is explicitly the lowest-value arm and is sized accordingly.

## 3. Design

Paired-by-seed, two models, same blind bundle (`benchmark/recover_v2/blind`, candidate table
`6ca33d4e…`).

| arm | conditions | n per condition | seeds |
|---|---|---|---|
| Q1 | `tool_llm`, `tool_llm_v2_ontology` | 20 | 5001-5020 |
| Q2 | `pur_agent_v2` | 20 | 5001-5020 |
| Q3 | four `pur_agent_v2_no_*` ablations | 10 | 5001-5010 |
| context | `direct_llm`, `pur_agent` | 10 | 5001-5010 |

Primary model `gpt-5.6-luna`; `gpt-5.5` repeats Q1 only (20+20), because Q1 is the claim that
must survive a second model and the others are not worth doubling.

Every condition in an arm uses the **same seed list**, so the comparison is paired and McNemar's
exact test on the discordant pairs is the appropriate analysis — not two independent
proportions. Predeclared: primary endpoint is `complete_decision_recovery` on the Q1 pair,
two-sided, alpha 0.05.

### Power

At the observed `tool_llm` rate of ~0.4 on `gpt-5.6-luna`, if the ontology lifts it to ~1.0 then
roughly 12 of 20 pairs are discordant in one direction and none in the other. McNemar reaches
p < 0.001 with far fewer than 20 pairs, so n=20 is comfortable even if the true effect is half
that size. Going to 50 buys precision on an effect that is already unambiguous, at 2.5x the
cost.

### Cost

Measured per-run from the pilot: `tool_llm` ~37 s and ~53k input tokens; `pur_agent_v2` ~77 s
and ~155k. The design above is 190 runs, roughly 2.5 hours of wall clock and ~15M input tokens.
The discarded "50 runs x 8 conditions x 2 models" plan is 800 runs, ~11 hours and ~60M input
tokens, to answer the same three questions less directly.

## 4. Rules that do not move

- Freeze the manifest with `scripts/freeze_run_manifest.py` on a clean worktree **before** the
  first run; it refuses to overwrite itself.
- Same run count and seed schedule within an arm. No condition is added, removed or retuned
  after results are visible.
- All runs kept: transport failures, invalid JSON, timeouts, negatives.
- No prompt, tolerance, objective, constraint or gold changes for any reason arising from
  these results. A demonstrated scientific-contract bug means versioning the benchmark and
  rerunning affected conditions, not patching in place.
- If Q2 shows no difference, that is the reported result. The paper's defensible claim is
  already strong without it: deterministic tooling converts an unreliable language-only
  baseline (0/3) into one that is scientifically correct 13/13, and a canonical interface
  removes the residual failure mode.

## 5. Commands

```bash
python scripts/freeze_run_manifest.py --label formal_v2_<date> --benchmark recover_v2 \
  --runs 20 --seed-base 5000 \
  --conditions direct_llm tool_llm tool_llm_v2_ontology pur_agent pur_agent_v2 \
               pur_agent_v2_no_evidence_planner pur_agent_v2_no_challenge \
               pur_agent_v2_no_cross_path pur_agent_v2_no_certificate
```

```bash
python scripts/run_baselines.py --conditions tool_llm tool_llm_v2_ontology pur_agent_v2 \
  --runs 20 --seed-base 5000 --blind-dir benchmark/recover_v2/blind \
  --results-root results/recover_v2/formal_v2_<date>
```

```bash
python scripts/run_baselines.py --conditions direct_llm pur_agent pur_agent_v2_no_evidence_planner \
  pur_agent_v2_no_challenge pur_agent_v2_no_cross_path pur_agent_v2_no_certificate \
  --runs 10 --seed-base 5000 --blind-dir benchmark/recover_v2/blind \
  --results-root results/recover_v2/formal_v2_<date>
```

```bash
python scripts/run_agent_benchmark.py --condition tool_llm --model gpt-5.5 --runs 20 \
  --seed-base 5000 --blind-dir benchmark/recover_v2/blind \
  --out-dir results/recover_v2/formal_v2_<date>/tool_llm/gpt-5.5
python scripts/run_agent_benchmark.py --condition tool_llm_v2_ontology --model gpt-5.5 --runs 20 \
  --seed-base 5000 --blind-dir benchmark/recover_v2/blind \
  --out-dir results/recover_v2/formal_v2_<date>/tool_llm_v2_ontology/gpt-5.5
```

```bash
python scripts/summarize_benchmark.py results/recover_v2/formal_v2_<date>
```
