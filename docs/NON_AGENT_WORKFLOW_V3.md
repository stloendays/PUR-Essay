# Non-Agent workflow v3

## Scientific question

How do chemistry, stoichiometry and temperature reshape HMPUR/prepolymer rheology, and how does that physical response propagate into a robust formulation decision?

## Layer 1 — evidence and protocol

Keep source, temperature, method and units explicit. Do not pool raw melt viscosities across sources before protocol harmonization.

## Layer 2 — rheological state compression

Fit each continuous viscosity curve with the Andrade form and represent the sample with a reference viscosity plus apparent activation energy `(eta120, Ea)`.

This separates two physical questions:

- how viscous is the formulation at a practical reference temperature?
- how rapidly does viscosity change with temperature?

## Layer 3 — local physical effects

Estimate only within matched chemistry blocks:

- %NCO -> eta_ref effect;
- %NCO -> Ea effect;
- polyol contrast at fixed isocyanate and %NCO;
- temperature amplification of chemistry contrast.

## Layer 4 — formulation interaction

Use near-factorial patent blocks to test whether a component shift has a transferable effect or is gated by the remaining blend composition. Report effect sizes and interaction contrasts, not unsupported significance tests.

## Layer 5 — decision propagation

Only after the physical trend layer is established should candidate ranking be propagated through feasibility and robustness constraints. Synthetic response surfaces may be used for algorithmic benchmarks but must not be cited as experimental evidence.

## Layer 6 — backward design

For each decision-frontier change, solve backward for the minimum composition/stoichiometry change needed to cross the active constraint and test whether that point lies on the admissible formulation manifold.

## Layer 7 — prospective experiment

The wet-lab experiment validates the already-frozen physical/decision prediction. It should report both absolute viscosity and temperature sensitivity, not a single temperature point alone.

## Agent separation

The Agent receives the frozen data/rules later and is scored on recovery. It does not define any physical result in Layers 1–7.
