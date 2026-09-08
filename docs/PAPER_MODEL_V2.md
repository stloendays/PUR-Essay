# Publication model v2

## Headline question

Can a source-grounded polyurethane design workflow define a unique constrained processing optimum from complete data, explain why that optimum sits where it does, and then have an answer-withheld scientific Agent independently recover the same decision before prospective laboratory validation?

## Contribution stack

1. Source-aware PUR/HMPUR data infrastructure.
2. Frozen complete-data oracle over a finite candidate space.
3. Backward constraint analysis of the selected formulation.
4. Blind Agent recovery with answer fields withheld.
5. Prospective wet-lab validation of the already-frozen optimum.

## Why this is stronger than v0.7/v1.1

The earlier workflow emphasized uncertainty and experiment selection. v2 changes the scientific task: the complete deterministic scenario first establishes an oracle benchmark, then the Agent is tested on whether it can faithfully recover that benchmark. This eliminates the conceptual ambiguity between 'the Agent chose a candidate' and 'the scientific workflow defined the optimum.'

The selected formulation is not the old broad-window optimum. Using the narrower literature-preferred viscosity region plus hard formulation constraints materially changes the optimum, providing a concrete objective-definition ablation.

## Key backward-design insight

The same 40/60 PPG400/PPG2000 blend at NCO:OH=1.6 is closer to the preferred property centers, but falls below the MDI mass-fraction floor. The admissible optimum shifts to NCO:OH=1.7. Thus the selected point is explained by intersection of a performance optimum with a formulation boundary rather than by a black-box maximum.

## Agent role

The Agent is secondary to the deterministic optimizer. It receives complete data and rules but not the answer. It is scored by exact recovery, rank regret, constraint compliance and fidelity of the backward explanation.

## Experimental role

The optimizer is frozen before synthesis. Wet-lab work only verifies the selected formulation's processing viscosities, viscosity ratio and batch reproducibility. Neighbor controls, if used, test local directional predictions; they are not search points.

## Main figure plan

1. Data/provenance map and finite design space.
2. Broad vs preferred windows and hard formulation constraints.
3. Candidate landscape and unique constrained optimum.
4. Backward NCO sweep, blend sweep and active MDI boundary.
5. Blind Agent benchmark across models/seeds.
6. Prospective wet-lab validation of the frozen optimum.
