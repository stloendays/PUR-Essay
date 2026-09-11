# Prospective wet-lab validation V6 — instrument-aware common-material plan

**Status:** current experimental execution plan. V6 retains the frozen five-formulation chemistry from V5 but adds an explicit instrument-window feasibility gate after laboratory feedback that the pre-MDI PPG2000/PDP-70 system is below the lower useful range of the available viscometer.

## 1. Frozen chemistry remains unchanged

Reactive system:

```text
PPG2000 + STEPANPOL PDP-70 + 4,4'-MDI
```

Five formulations remain unchanged:

| Role | PPG2000 / PDP-70 (polyol wt parts) | NCO:OH | Main question |
|---|---:|---:|---|
| N- | 50 / 50 | 1.70 | lower-stoichiometry response |
| CTR | 50 / 50 | 1.80 | centre/reference |
| N+ | 50 / 50 | 1.90 | higher-stoichiometry response |
| C-P | 60 / 40 | 1.80 | PPG2000-rich response |
| C-E | 40 / 60 | 1.80 | PDP-70-rich response |

Replication remains:

```text
5 formulations x 3 independent synthesis batches = 15 independent syntheses
```

No third polyol or other raw material is added merely to make a viscosity instrument return a value, because that would change the formulation identity and the hypothesis.

## 2. New measurement-feasibility gate

Before assigning a temperature point to the formal rheology dataset, verify that the expected or observed viscosity is inside the calibrated range of the selected instrument/geometry.

Required metadata:

- instrument model;
- spindle/geometry;
- rotational speed or shear condition;
- lower reliable torque/viscosity limit;
- sample volume;
- sample temperature;
- conditioning history.

Decision rule:

```text
inside calibrated range -> report quantitative viscosity
below lower range -> report left-censored / below-range status
above upper range -> report right-censored / above-range status
```

Never encode below-range as zero and never silently drop it as ordinary missing data.

## 3. Revised pre-MDI plan

The V5 requirement to measure the pre-MDI blend directly at 80/90/100/110/120 C is removed as an unconditional requirement.

Reason: for ordinary polyol liquids, viscosity decreases with increasing temperature. If the blend is already below the useful range of the available viscometer at a lower temperature, heating further will generally worsen measurability on that same setup.

Pre-MDI execution therefore becomes:

1. run a short measurability screen at the lowest scientifically relevant liquid-state temperature available to the laboratory;
2. if measurable, build a temperature series within the instrument window;
3. if not measurable, use a validated low-viscosity adapter, cone-plate rheometer, capillary method, or equivalent lower-viscosity-capable method;
4. if no suitable hardware is available, retain the result as a censored feasibility observation rather than inventing a viscosity value.

A lower-temperature pre-MDI series may be used when scientifically valid, but it must not be presented as equivalent to a high-temperature process-viscosity series.

## 4. Post-MDI plan

The NCO-terminated prepolymer remains the primary process-relevant rheology target.

The original candidate temperature window remains:

```text
80 / 90 / 100 / 110 / 120 C
```

but each point must first pass the instrument-window gate. If all points are measurable, fit:

```text
ln(eta) = A + B/T
Ea,app = R * B
```

If one or more points are censored, do not force an ordinary least-squares Andrade fit across fabricated values. Use only measurable points for descriptive fitting and retain censoring flags explicitly.

## 5. Scientific comparisons retained

The primary comparisons remain:

- N- -> CTR -> N+: local NCO:OH response;
- C-P -> CTR -> C-E: polyether/polyester composition response;
- pre-MDI vs post-MDI: whether reaction amplifies or reshapes rheology, but only where both stages are quantitatively measurable;
- batch-to-batch reproducibility.

If pre-MDI quantitative measurement is not possible with available hardware, the pre/post comparison is downgraded from a primary quantitative endpoint to an instrument-feasibility observation. The post-MDI rheology study remains valid.

## 6. Agent / workflow implication

The experimental workflow now contains a separate measurement-feasibility layer:

```text
candidate generation
-> chemistry/process feasibility
-> instrument-window feasibility
-> wet-lab execution
-> evidence update
```

This distinction is important: a formulation can be chemically/process feasible but experimentally unmeasurable with a particular instrument. The Agent should not reject such a formulation as chemically invalid; instead it should recommend an appropriate measurement method or record a censored observation.

## 7. Database link

The corresponding staging-layer records are stored in `stloendays/Database-For-PUR`:

- `data/materials/BATCH_017.md`
- `data/materials/batch017_experimental_measurability_constraints.csv`

V5 is retained as the historical pre-feedback plan. V6 is the current instrument-aware execution version.
