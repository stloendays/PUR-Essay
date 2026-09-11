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

---

# Q1 result — does the canonical ontology remove the failure mode?

Executed 2026-09-11 against the frozen manifest
(`results/recover_v2/formal_v2_20260911/run_manifest.json`, commit `986b9637`, clean worktree).
Paired by seed, 5001-5020, same bundle, same prompt, same tool policy, no gate in either arm.
The two conditions differ in exactly one respect: the constraint vocabulary their tools emit.

| model | condition | complete | scientifically correct | canonical spelling |
|---|---|---|---|---|
| `gpt-5.6-luna` | `tool_llm` | 15/20 | 20/20 | 15/20 |
| `gpt-5.6-luna` | `tool_llm_v2_ontology` | **20/20** | 20/20 | 20/20 |
| `gpt-5.5` | `tool_llm` | 10/20 | 19/20 | 10/20 |
| `gpt-5.5` | `tool_llm_v2_ontology` | **20/20** | 20/20 | 20/20 |

McNemar, exact, two-sided, predeclared alpha 0.05:

| model | both | neither | ontology wins | `tool_llm` wins | p |
|---|---|---|---|---|---|
| `gpt-5.6-luna` | 15 | 0 | 5 | **0** | 0.0625 — **does not reach alpha** |
| `gpt-5.5` | 10 | 0 | 10 | **0** | **0.00195 — reaches alpha** |

Zero reversals in 40 paired runs across both models.

## The luna arm was underpowered, and that is my estimation error

The design sized Q1 at n=20 from the probe's `tool_llm` rate of 0.4 on `gpt-5.6-luna`,
predicting ~12 discordant pairs. On seeds 5001-5020 that condition ran at 0.75, producing only
5. With 5 discordant pairs all in one direction the exact two-sided p is 2/2^5 = 0.0625, which
is the *smallest value the test can return* at that count — n=20 could not have reached 0.05
for this effect no matter how clean the direction was.

No repair was applied. The test was not switched to one-sided, alpha was not moved, and the
probe runs were not pooled in after the fact. The `gpt-5.5` arm that does reach alpha was part
of the frozen design before any Q1 run, not added in response to the luna p-value. No pooling
rule across models was predeclared, so the two arms are reported separately and no combined
statistic is computed.

## What every failure was

All 15 `tool_llm` failures across both models are the constraint name. Not one is a winner, a
threshold, a grid point, a reachability verdict or a trend.

```text
mdi_fraction_min                      x 4   (gpt-5.6-luna; copied from the V1 tool's own output)
mdi_fraction_of_polyol_plus_mdi       x 10  (1 luna, 9 gpt-5.5; copied from the raw config key)
mdi_fraction_of_polyol_plus_mdi_min   x 1   (gpt-5.5 seed 5008)
```

In every one of those 15 cases the paired `tool_llm_v2_ontology` run, same seed, recovered the
complete chain.

## One unregistered spelling, deliberately left unregistered

`gpt-5.5` seed 5008 wrote `mdi_fraction_of_polyol_plus_mdi_min` — a fourth spelling of the same
constraint, and the only one not in the alias table. `same_constraint` therefore returns False
and the run is scored `scientific_correctness = False`, which is why that arm reads 19/20 rather
than 20/20. Its own evidence string says "all nominal hard constraints passed except
mdi_fraction", so this is transparently the same constraint.

**The alias table was not extended.** Registering a spelling after seeing it fail is exactly the
retroactive aliasing that §8 of `AGENT_WORKFLOW_V2.md` forbids — an ontology change must be made
before a matrix and applied to every condition, not patched in once results are visible. It
would also have moved a *baseline* number, which is no more legitimate than moving an Agent one.
The 19/20 stands as measured. If the ontology is versioned later, the change belongs in a new
ontology version applied to all conditions and rerun, and this run is the evidence motivating it.

Note that the primary metric is unaffected either way: that run fails
`active_constraint_recovery` against the frozen gold under any alias policy.

## Reading

Q1 is answered on `gpt-5.5` and directionally consistent but underpowered on `gpt-5.6-luna`.
The canonical ontology removes the failure mode: 40/40 across both models, against 25/40 for the
identical setup differing only in vocabulary.

This is an interface result, not a reasoning result, and should be stated that way. With
deterministic tools this model recovers the science essentially always; what it does not do
reliably is name the constraint the way the frozen contract names it, and it fails that most
often by copying a string the tool itself handed it.

## Status of the rest of the matrix

Q2 (`pur_agent_v2`, n=20) and Q3 (the four gate ablations, n=10) are declared in the same frozen
manifest and have **not** been executed. The manifest records all nine conditions; only the two
Q1 conditions have run. Any later execution uses the same manifest and the same seeds.
