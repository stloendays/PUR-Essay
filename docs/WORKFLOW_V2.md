# PUR-Oracle v2 workflow

## Scientific role

The deterministic workflow, not an LLM, defines the formulation optimum. The Agent is evaluated only after the gold solution is frozen. The laboratory does not search the design space; it validates the workflow-selected formulation against preregistered property targets.

The guarantee is scoped: v2 returns the unique optimum inside the frozen 928-candidate design space under the frozen objective and constraints. It does not claim a mathematical global optimum over all possible polyurethane chemistry.

## Complete-data oracle

Hard constraints are applied before ranking: broad functional viscosity window; narrower preferred viscosity windows; NCO:OH 1.3-3.0; MDI 35-49 wt% of polyol+MDI; chemistry-in-domain; and full oracle interval inside the broad viscosity window.

Among feasible candidates, the objective is equal-weight squared log-distance to geometric centers of the preferred windows:

`J=[log10(eta80/eta80*)]^2+[log10(eta120/eta120*)]^2+[log10(ratio/ratio*)]^2`

with eta80*=3.4785 Pa.s, eta120*=0.4243 Pa.s and ratio*=8.1548.

## Frozen optimum

`WO_INV_0579`: 40 parts PPG400 + 60 parts PPG2000, NCO:OH=1.7 and 55.30525 parts 4,4'-MDI per 100 parts polyol. Oracle response: eta80=3.4427 Pa.s, eta120=0.4098 Pa.s, ratio=8.4016.

## Backward analysis

For the same 40/60 blend, NCO:OH=1.6 is numerically closer to the preferred property centers but corresponds to 34.23 wt% MDI and violates the frozen 35 wt% lower bound. NCO:OH=1.7 is the first admissible point on this trajectory. At fixed NCO:OH=1.7, lower PPG400 fractions push viscosity upward; higher PPG400 fractions push viscosity downward. The 40/60 composition is the discrete joint balance point under the hard mass-fraction constraint.

## Blind Agent benchmark

The Agent sees the complete candidate responses and frozen rules but not oracle score, rank, best flag or gold candidate ID. Metrics are exact top-1 recovery, oracle rank, objective regret, hard-constraint violations and explanation fidelity for the active boundary and local response directions.

## Wet-lab role

Experiments verify the already-frozen optimum. They do not choose among formulations. Use independent synthesis batches to test eta80, eta120 and eta80/eta120 against preregistered preferred windows.
