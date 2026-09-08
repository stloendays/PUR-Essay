# PUR-Oracle v2

A deterministic polyurethane inverse-design workflow built around four separable layers:

**complete-data oracle -> backward constraint analysis -> blind Agent recovery -> prospective wet-lab validation**

The optimizer, not the LLM, owns the scientific answer. The Agent is evaluated only after the gold solution is frozen.

## Frozen conceptual optimum

Within the 928-candidate WO2018173768-inspired PPG/4,4'-MDI design space, v2 applies literature-derived preferred viscosity targets plus hard chemistry/process constraints. **117 candidates pass all hard gates.** The unique optimum is:

- candidate: `WO_INV_0579`
- PPG400 / PPG2000 = `40 / 60` parts
- NCO:OH = `1.7`
- 4,4'-MDI = `55.30525` parts per 100 polyol parts
- MDI fraction of polyol + MDI = `35.61 wt%`
- oracle eta80 = `3.4427 Pa.s`
- oracle eta120 = `0.4098 Pa.s`
- eta80/eta120 = `8.4016`

Preferred-window geometric centers are 3.4785 Pa.s, 0.4243 Pa.s and 8.1548.

## Why this point is selected

Backward analysis shows that the same 40/60 blend at NCO:OH=1.6 is even closer to the property centers, but its MDI fraction is only 34.23 wt% and fails the frozen 35 wt% lower bound. The constrained optimum therefore moves to NCO:OH=1.7. At fixed NCO:OH=1.7, changing the PPG400/PPG2000 ratio in either direction moves the response away from the joint preferred center.

This is a **constraint-intersection optimum**, not a black-box guess.

## Workflow

1. Freeze the complete candidate response table and literature-derived constraints.
2. Exhaustively rank the full finite design space.
3. Freeze the unique conceptual optimum.
4. Run backward analysis to identify active constraints and local response directions.
5. Hide oracle score/rank/gold ID from the Agent while keeping the complete data and rules visible.
6. Benchmark whether the Agent recovers the same optimum and explanation.
7. Use wet-lab experiments only to validate the already-frozen optimum and predicted property windows.

## Active v2 files

- `configs/oracle_v2.json` - frozen constraints and objective.
- `data/oracle_top30_compact.csv` - compact audit snapshot of the highest-ranked candidates.
- `results/oracle_v2/oracle_best.json` - frozen gold optimum.
- `docs/WORKFLOW_V2.md` - scientific workflow.
- `docs/PAPER_MODEL_V2.md` - manuscript architecture.
- `docs/AGENT_BLIND_BENCHMARK_V2.md` - answer-withheld Agent evaluation.
- `docs/VALIDATION_EXPERIMENT_V2.md` - experiment-as-validation specification.

## Claim boundary

`PUR_SIM_V1` is a deterministic benchmark scenario, not wet-lab evidence. v2 guarantees the unique optimum only inside the frozen candidate space, objective and constraints. Prospective experiments determine whether that model-defined optimum transfers to physical polyurethane behavior.
