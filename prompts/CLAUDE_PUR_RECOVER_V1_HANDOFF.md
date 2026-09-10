# Copy-paste prompt for local Claude — PUR-RECOVER V1 (CURRENT)

You are taking over the **current formal Agent implementation / audit / real-API benchmark phase** of:

`https://github.com/stloendays/PUR-Essay`

Start from a fresh `git pull origin main`. Do not continue from your previous project memory until you have read the current repository state.

---

## 0. CRITICAL CORRECTION TO YOUR PREVIOUS AUDIT

Your previous report said the complete 928-row `PUR_SIM_V1` response table was missing. **That statement is now obsolete.**

The original uploaded historical archive was re-audited and two distinct 928-row tables were found:

- old v0.7 ML table: `v07_wo_inverse_design_candidates.csv`;
- deterministic synthetic `PUR_SIM_V1` table: `v07_wo_inverse_design_candidates_模拟.csv`.

The recovered 51-column PUR_SIM_V1 table explicitly contains `simulation_protocol_id = PUR_SIM_V1`, `synthetic_scenario = True`, simulated eta80/eta120/ratio, interval radius and domain diagnostics.

Its canonical 14-column projection serializes to SHA256:

`d8623116c6a2f60c9e022e52eeb6540573dd9434b5e507c79701abb55635bcd9`

which is exactly the hash frozen by the current repository snapshot/manifest. Therefore:

**DO NOT ask me to manually supply the 928 response table.**

On a fresh clone, the repository must reconstruct/materialize it from the multipart frozen snapshot and verify the hash before using it.

Read first:

- `docs/PUR_SIM_V1_RECOVERY_AUDIT.md`
- `data/pur_sim_v1/PROVENANCE.json`
- `data/pur_sim_v1/README.md`
- `src/pur_science/dataio.py`
- `results/frontier_v1/manifest.json`

If reconstruction/hash verification fails, stop. Never synthesize replacement responses.

### Important claim boundary

We **do still use the 928-candidate PUR_SIM_V1 benchmark**, but only for:

- deterministic finite-space decision analysis;
- L0/L1/L2 ranking;
- constraint / uncertainty phase analysis;
- backward reachability;
- the blinded Agent recovery benchmark.

We **do not use PUR_SIM_V1 as empirical evidence for real polyurethane rheology**. Real rheology claims come from public/experimental source data and prospective wet-lab validation.

So the current architecture is not “remove the 928 dataset”. It is:

```text
real/source-grounded rheology science       -> physical claims
hash-verified PUR_SIM_V1 928 benchmark      -> decision/Agent claims
prospective wet lab                         -> physical transferability
```

Keep those evidence layers strictly separated.

---

## 1. CURRENT PAPER AGENT VS HISTORICAL AGENT

There are two Agent code paths.

### CURRENT PAPER AGENT

- `src/pur_agent/`
- benchmark: `PUR_RECOVER_V1`
- role: **blinded scientific decision recovery**

### HISTORICAL AGENT — NOT THE CURRENT PAPER AGENT

- `src/pur_bridge/agent.py`
- `E6_star`
- information gain
- active-learning experiment selection
- material-equivalence-gate-led experiment choice
- post-E6 adaptive experiment selection

If your previous implementation work centered on E6, information gain or “choose the next experiment”, retain it only as historical provenance. Do not delete it, but do not continue the current paper from it.

Reusable engineering pieces such as API transport, retries, structured parsing or logging may be ported only after you verify that they do not change the current scientific contract or leak gold.

---

## 2. CURRENT PAPER ARCHITECTURE

The LLM does not define the scientific answer.

```text
source-grounded real rheology
 -> deterministic PUR-FRONTIER V1
 -> FRONTIER-DEPTH deterministic analyses
 -> freeze evaluator gold
 -> anonymise / withhold answers
 -> PUR-RECOVER V1 Agent + baselines + ablations
 -> evaluator-only scoring
 -> prospective wet-lab validation
```

The current manuscript figure order is:

```text
Figure 2  real Andrade / Ea rheology
Figure 3  free-NCO coupling
Figure 4  low-temperature amplification / context interaction / published rank reversal
Figure 5  deterministic L0/L1/L2 decision frontier + backward boundary + MDI phase behavior
Figure 6  uncertainty phase transition + robustness cliff + objective geometry
Figure 7  REAL-API PUR-RECOVER repeated benchmark
Figure 8  prospective wet-lab validation
```

Do not put mock Agent results into Figure 7. Do not put wet-lab data into the Agent context.

---

## 3. FROZEN DETERMINISTIC SCIENTIFIC CONTRACT

The current evaluator-side decision chain is encoded by `configs/frontier_v1.json` and deterministic `src/pur_science/`.

Expected frozen results are:

```text
L0 property winner      WO_INV_0419
L1 constrained winner   WO_INV_0579
L2 robust winner        WO_INV_0420
active boundary         MDI fraction >= 0.35
backward threshold      NCO:OH = 1.7719836724
first reachable grid    NCO:OH = 1.8
```

These IDs are evaluator-side facts and must never be shown to the anonymised model-under-test.

### CURRENT L2 ROBUST DEFINITION — DO NOT USE YOUR OLD VERSION

Your previous report described a robust rule requiring the entire uncertainty interval to lie inside the **preferred** window. That is no longer the current frozen definition.

Read `configs/frontier_v1.json` directly. Current L2 is:

1. candidate must first pass L1 nominal feasibility;
2. propagated full uncertainty intervals must remain inside the **broad functional windows**;
3. `domain_ratio <= 1.0`;
4. among those candidates, minimize the exact worst-case value of the same frozen log-space objective;
5. uncertainty log-radius multipliers are `(1, 1, 2)` for eta80, eta120 and eta80/eta120;
6. preferred windows define the optimisation target, **not** the robust certification envelope;
7. `require_interval_inside_preferred = false`.

Do not duplicate this scoring rule in Agent code. Agent tools must delegate to the canonical deterministic implementation in `pur_science`.

Do not tune uncertainty weights, windows, MDI limits, objective weights or evaluator tolerances after seeing model performance.

---

## 4. CURRENT AGENT ROLE

PUR-RECOVER V1 is a **blinded scientific decision-recovery system**.

The Agent is not asked to invent a formulation or search the chemical universe. It is asked to recover a previously frozen decision chain from the blind admissible benchmark using approved deterministic tools.

A complete successful run must recover, using anonymised candidate labels:

1. property-only winner;
2. nominal constrained winner;
3. robust winner;
4. active constraint;
5. continuous backward threshold;
6. first reachable grid value;
7. reachability verdict;
8. local NCO direction;
9. local composition direction.

A lucky final-winner guess is not complete recovery.

Primary metric:

`complete_decision_recovery`

Diagnostics must include at least:

- Top-1 / Top-3 / Top-5;
- recovered deterministic rank;
- objective regret;
- hard-constraint violations;
- backward-threshold absolute error;
- reachability accuracy;
- explanation fidelity;
- tool-call count;
- API-call count;
- token usage;
- latency;
- invalid JSON/schema failures;
- transport/time-out failures.

---

## 5. CURRENT AGENT STRATEGY STACK

Preserve or implement the following strategy before formal runs. The LLM plans/interprets; deterministic numerical truth remains in tools.

### A. Answer withholding + anonymisation

Primary candidate IDs become `Candidate_XXXX`; source polyol identities become anonymous `Polyol_*` labels. Evaluator mapping is inaccessible to the model.

Named chemistry is secondary only and must never replace the primary anonymised benchmark.

### B. Plan -> inspect -> constrain -> robust rank -> backward -> local sweep -> verify -> final

The full `pur_agent` should execute a staged decision process rather than one-shot prose:

1. inspect benchmark/provenance metadata;
2. inspect candidate-space/schema sanity;
3. recover L0 property ranking using deterministic tool;
4. recover L1 feasibility / active constraint;
5. recover L2 robust ranking under the frozen rule;
6. solve backward threshold and project onto reachable grid;
7. inspect local NCO/composition trends;
8. reconcile evidence/tool outputs;
9. run a final consistency/self-check;
10. emit only the structured final schema.

### C. Deterministic tool grounding

The LLM must not do 928-row arithmetic mentally. Ranking, feasibility, interval propagation, backward solve, reachability and local sweeps must delegate to deterministic wrappers backed by `pur_science`.

### D. Trace gating

For full `pur_agent`, finalisation should be blocked until the required tool families have been used/inspected. Ablations must remove both the relevant tool and its corresponding trace requirement, so they remain executable and scientifically interpretable.

### E. Structured-output/schema enforcement

Final output must conform to the declared decision schema. If transport/provider formatting differs, adapt the client/parser layer without changing the scientific task.

Schema retries may repair malformed output, but do not silently reinterpret or replace scientifically wrong answers.

### F. Independent evaluator

Agent run first; evaluator reads gold only afterwards. Never expose evaluator mapping/gold through retrieval, tool filesystem, error strings or prompts.

### G. Immutable run evidence

Every run record must preserve:

- run ID;
- condition;
- model/provider;
- prompt/data/config hashes;
- anonymisation seed;
- LLM seed if applicable;
- tool trace;
- raw final text;
- parsed structured decision;
- response IDs where available;
- usage/tokens;
- latency;
- API/schema/tool errors;
- evaluation metrics after evaluator pass.

Never delete bad runs from formal results.

### H. Failure-aware benchmark design

Keep a failure taxonomy at least for:

- wrong property ranking;
- wrong constraint logic;
- wrong robust decision;
- backward/reachability failure;
- local-trend failure;
- provenance failure;
- tool-use failure;
- invalid schema/JSON;
- API/transport failure.

### I. No post-hoc rescue

After formal runs begin, do not retune prompts, tool access, tolerance, seeds or scientific rules based on visible results. If a scientific-contract bug is real, version a new benchmark and rerun all comparable conditions from scratch.

---

## 6. BLINDNESS / GOLD-LEAKAGE CONTRACT

Primary model-under-test may receive only the generated blind bundle under:

`benchmark/recover_v1/blind/`

plus approved prompts and deterministic tool interfaces.

It must not read or receive content from:

- `benchmark/recover_v1/evaluator_only/`;
- `gold/recover_v1/`;
- `results/frontier_v1/`;
- `results/frontier_depth_v1/`;
- manuscript passages that reveal gold IDs;
- `data/prospective_validation/`;
- current wet-lab result files when they eventually exist.

Also guard against indirect leakage through:

- exceptions/error messages;
- debug logs;
- tool descriptions;
- file paths containing mappings;
- cached prompts;
- retrieval context;
- summary files.

Developer/evaluator-side code may know where gold lives. The model-under-test context may not.

---

## 7. CONDITIONS THAT MUST REMAIN COMPARABLE

Preserve:

- `oracle` — deterministic reference, not an LLM competitor;
- `direct_llm` — language-only baseline;
- `tool_llm` — tools without the full strategy guard;
- `pur_agent` — full staged/trace-gated Agent;
- `pur_agent_no_backward`;
- `pur_agent_no_constraint_checker`;
- `pur_agent_no_provenance`;
- `pur_agent_single_pass`.

Do not remove a negative condition because it performs poorly.

Ablations should isolate one capability as cleanly as practical. If you discover an ablation is confounded, document it before formal runs rather than changing it after seeing results.

---

## 8. CURRENT WET-LAB PLAN — KEEP OUT OF THE AGENT

The current experiment is no longer the historical `WO_INV_0579` single-point plan.

Current source of truth:

`docs/VALIDATION_EXPERIMENT_V3.md`

It is centered on `WO_INV_0420` and uses the five-formulation local matrix:

```text
N-   WO_INV_0419   50/50 PPG700/PPG1000   NCO:OH 1.70
OPT  WO_INV_0420   50/50                   NCO:OH 1.80
N+   WO_INV_0421   50/50                   NCO:OH 1.90
C-   WO_INV_0404   60/40                   NCO:OH 1.80
C+   WO_INV_0436   40/60                   NCO:OH 1.80
```

Each has 3 independent synthesis batches, with paired pre-MDI/post-MDI rheology at 80/90/100/110/120 C.

This wet-lab design is **prospective physical validation only**. It must not be used to tune the Agent or appear in the primary blind input.

---

## 9. FIRST READ THESE FILES IN THIS ORDER

1. `README.md`
2. `docs/AGENT_HANDOFF_CURRENT.md`
3. `docs/AGENT_STRATEGY_V1.md`
4. `docs/PUR_SIM_V1_RECOVERY_AUDIT.md`
5. `configs/frontier_v1.json`
6. `configs/recover_v1.json`
7. `docs/FRONTIER_V1.md`
8. `docs/FRONTIER_DEPTH_V1.md`
9. `docs/VALIDATION_EXPERIMENT_V3.md`
10. `manuscript/NON_AGENT_RESULTS_V2.md`
11. `src/pur_science/`
12. `src/pur_agent/`
13. `scripts/build_blind_bundle.py`
14. `scripts/verify_no_leakage.py`
15. `scripts/run_agent_once.py`
16. `scripts/run_agent_benchmark.py`
17. `scripts/run_baselines.py`
18. `scripts/evaluate_agent_runs.py`
19. `scripts/summarize_benchmark.py`
20. current `prompts/`
21. relevant `tests/`

Only after this, inspect `src/pur_bridge/agent.py` to classify old E6 work as historical.

---

## 10. PHASE A — AUDIT BEFORE MODIFYING

Before writing code, produce a current audit answering:

1. Which parts of PUR-RECOVER V1 are complete?
2. Which are partial or brittle?
3. Does any current code still route through `pur_bridge` / E6 logic?
4. Is 928 reconstruction/hash verification actually automatic on your fresh clone?
5. Does the computed deterministic frontier reproduce the frozen L0/L1/L2 and backward values?
6. Is the current L2 implementation exactly the broad-window worst-case definition from `configs/frontier_v1.json`?
7. Is there any direct or indirect gold leakage path?
8. Are prompts, schemas, tools, strategy checks, evaluator and run scripts internally consistent?
9. Does each ablation isolate the intended capability?
10. Does provider/API transport preserve tool calling, structured output and usage/logging semantics?
11. Which findings are ordinary implementation bugs?
12. Which would alter the scientific contract and therefore require a new benchmark version?

Create/update an audit document in the repository. Do not rewrite working code merely for style.

---

## 11. PHASE B — REPRODUCE DETERMINISTIC SCIENCE

Run:

```bash
git pull origin main
python -m venv .venv
# activate for current OS
pip install -e ".[agent,dev]"
pytest -q
python scripts/freeze_frontier_v1.py
python scripts/analyze_frontier_depth_v1.py
```

Required checks:

- 928 rows reconstructed;
- frozen SHA256 verified;
- no substitution with old v0.7 responses;
- L0/L1/L2 reproduced;
- backward threshold reproduced;
- expected candidate counts reproduced;
- no code patching to force expected winners.

If any of these fail, STOP and report before API work.

---

## 12. PHASE C — BUILD AND ATTACK-TEST THE BLIND BUNDLE

Run:

```bash
python scripts/build_blind_bundle.py
python scripts/verify_no_leakage.py
```

Then manually/adversarially inspect the generated blind directory.

Search for leakage of:

- `WO_INV_`;
- source PPG labels if primary chemistry is anonymised;
- `oracle_score`;
- `oracle_rank`;
- `oracle_is_best`;
- gold IDs;
- mapping content;
- ordered answer lists;
- explicit winner text;
- wet-lab/prospective validation outputs.

Also verify that tool runtime cannot traverse into evaluator/gold/results paths.

Document blind-bundle hashes and anonymisation seed.

---

## 13. PHASE D — OFFLINE SMOKE ONLY

Run:

```bash
python scripts/run_agent_once.py --provider mock --condition pur_agent
python scripts/run_baselines.py --runs 2 --provider mock
python scripts/evaluate_agent_runs.py results/recover_v1
python scripts/summarize_benchmark.py
```

Mock is infrastructure validation only. Never report mock performance as manuscript Agent performance.

---

## 14. PHASE E — REAL API INTEGRATION

I will configure credentials locally using environment variables only:

```text
OPENAI_API_KEY
OPENAI_BASE_URL   # optional OpenAI-compatible endpoint
OPENAI_MODEL
OPENAI_PROVIDER   # optional
```

Never ask me to paste the real key into source, prompt, Git or run JSON.

First perform a minimal connectivity/tool-call/schema test. If the provider lacks a Responses-API feature, modify only the transport/client compatibility layer. Do not modify scientific objective, constraints, tool semantics or evaluator just to fit a provider.

Record provider/model identifiers and response IDs where available.

---

## 15. PHASE F — REAL-API PILOT

Start small:

```bash
python scripts/run_baselines.py \
  --conditions direct_llm tool_llm pur_agent \
  --runs 5
```

Also run deterministic oracle once.

Use a declared seed schedule and preserve every failure.

Pilot report must include:

- complete-decision-recovery rate;
- Top-1/3/5;
- L0/L1/L2 component success;
- backward/reachability success;
- constraint violation rate;
- explanation fidelity;
- tool/API calls;
- tokens;
- latency;
- schema/transport failure rates;
- failure taxonomy;
- exact git commit;
- prompt/config/data hashes.

If pilot reveals an implementation bug, fix it and restart all affected conditions. If the model is simply weak, keep the negative result.

---

## 16. PHASE G — FREEZE FORMAL BENCHMARK BEFORE LARGE RUNS

Before formal repeated runs, write a preregistration-style run manifest freezing:

- git commit SHA;
- benchmark ID/version;
- prompt hashes;
- config hashes;
- blind data hashes;
- 928 snapshot hash;
- anonymisation seed;
- model/provider exact identifiers;
- seed schedule;
- run count per comparable condition;
- max rounds;
- tool policy;
- evaluator tolerance;
- retry policy;
- handling of API/schema failures.

Only after this manifest exists should formal repeated API runs begin.

---

## 17. PHASE H — FORMAL REPEATED BENCHMARK

If budget permits, target 30-50 independent runs per comparable LLM condition. If budget is tighter, use the same predeclared smaller N for every comparable condition and report uncertainty honestly.

Core:

```text
direct_llm
tool_llm
pur_agent
```

Ablations:

```text
pur_agent_no_backward
pur_agent_no_constraint_checker
pur_agent_no_provenance
pur_agent_single_pass
```

Raw run JSON files are immutable evidence. Never overwrite/delete scientifically bad runs.

---

## 18. PHASE I — EVALUATION, UNCERTAINTY AND FIGURE 7 DATA

After all runs:

```bash
python scripts/evaluate_agent_runs.py results/recover_v1
python scripts/summarize_benchmark.py
```

Produce:

1. per-run long-format CSV/JSON;
2. condition-level summary CSV/JSON;
3. bootstrap or binomial uncertainty intervals for recovery rates where appropriate;
4. failure taxonomy table;
5. cost/latency table;
6. Figure 7-ready data only from real API runs.

At minimum include:

- condition;
- model;
- N;
- complete decision recovery;
- property/L1/L2 component recovery;
- Top-1/3/5;
- rank/regret;
- constraint violation;
- backward error/success;
- reachability accuracy;
- explanation fidelity;
- tool calls;
- API calls;
- tokens;
- latency;
- invalid schema count;
- API/transport failure count.

Do not fabricate missing values and do not merge mock runs with real runs.

---

## 19. WHAT YOU MAY IMPROVE WITHOUT CHANGING THE SCIENTIFIC CONTRACT

Before formal freeze, you may improve:

- provider/API compatibility;
- function/tool-call plumbing;
- explicit staged plan state;
- trace gating;
- final self-check logic;
- schema validation/retry plumbing;
- retry/error accounting;
- run-record provenance;
- leakage guards;
- ablation isolation;
- benchmark orchestration;
- evaluation summaries;
- confidence intervals / Figure 7-ready tables.

But deterministic numerical calculations must remain delegated to `pur_science` rather than being recreated inside the LLM strategy layer.

---

## 20. DO NOT DO THESE THINGS

- Do not say the complete PUR_SIM_V1 928 response table is still missing unless the current hash reconstruction actually fails.
- Do not substitute the old v0.7 928 predictions for PUR_SIM_V1.
- Do not remove the 928 benchmark from the current Agent study.
- Do not use the 928 synthetic responses as experimental rheology evidence.
- Do not revive E6/information-gain experiment selection as the current Agent task.
- Do not perform active learning over 928 as the primary benchmark.
- Do not require uncertainty intervals to lie inside preferred windows; use the current frozen broad-window robust definition.
- Do not duplicate scoring formulas in `pur_agent`.
- Do not show source candidate IDs/gold ranks/gold scores to the model-under-test.
- Do not give primary Agent named PPG chemistry unless explicitly running the secondary named-chemistry benchmark.
- Do not use manuscript text containing gold answers as retrieval context.
- Do not put V3 wet-lab measurements into the Agent bundle.
- Do not tune Agent prompts after formal outcomes are visible.
- Do not discard failed runs.
- Do not commit API keys.

---

## 21. FINAL DELIVERABLES BACK TO ME

Return:

1. correction of your previous “928 missing” conclusion with evidence from the current recovery audit;
2. old E6 Agent vs current PUR-RECOVER architecture audit;
3. list of changed files and exact reasons;
4. exact commands executed;
5. pytest / deterministic reconstruction / leakage results;
6. verification that current L2 matches `configs/frontier_v1.json` broad-window rule;
7. API transport/tool/schema status;
8. 5-run pilot results for core conditions;
9. formal run manifest;
10. formal repeated results if executed;
11. failure taxonomy;
12. Figure 7-ready per-run + summary data paths;
13. exact git commit SHA;
14. any issue that changes the scientific contract and would require a new benchmark version.

Do not tell me the Agent phase is complete merely because one run recovers the final winner. The manuscript claim requires **blinded, repeated, auditable complete-decision recovery** under the frozen scientific contract.
