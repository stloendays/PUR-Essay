# Blind Agent benchmark v2

The evaluator freezes the gold candidate before any Agent run.

## Agent receives

- complete candidate response/descriptor table;
- frozen constraints and objective;
- source/provenance documentation.

## Agent does not receive

- oracle score;
- oracle rank;
- best-candidate flag;
- gold candidate ID.

## Required output

One candidate ID plus a backward explanation covering property-center proximity, the active formulation constraint, the local NCO/OH direction and the local blend-ratio direction.

## Quantitative metrics

1. exact top-1 recovery;
2. oracle rank;
3. objective regret;
4. hard-constraint violation count;
5. explanation fidelity against frozen backward-analysis facts.

A successful Agent does not create the scientific truth; it recovers and explains a truth already defined by the deterministic workflow.
