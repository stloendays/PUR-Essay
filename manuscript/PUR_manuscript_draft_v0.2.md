# From Temperature-Amplified Rheology to Auditable Formulation Decisions in Polyurethane Prepolymers

## Source-grounded rheology, backward design, and blinded scientific-agent recovery

## Abstract

Polyurethane prepolymer viscosity is often represented by measurements at one or several processing temperatures, although formulation variables can affect not only the viscosity magnitude but also its temperature sensitivity. Here, we develop a source-grounded and decision-aware framework for polyurethane prepolymer design that separates experimentally supported rheological conclusions from deterministic inverse-design benchmarks and blinded scientific-Agent evaluation. A curated experimental dataset comprising 39 polyurethane prepolymers and 4,559 temperature-viscosity measurements was first analyzed using the Andrade relation, ln(eta) = A + B/T. The median fit R2 was 0.9967, and 37 of 39 formulations exhibited R2 >= 0.98. Despite this common functional form, the apparent flow activation energy varied from 34.74 to 94.15 kJ mol-1, demonstrating formulation-dependent thermal sensitivity. Within matched polyol/isocyanate families, increasing free NCO systematically lowered viscosity. Across 11 high-quality matched families, a one-percentage-point increase in free NCO produced median viscosity multipliers of 0.742 at 80 degC and 0.783 at 120 degC, while the apparent activation energy decreased by a median of 0.81 kJ mol-1 per percentage point NCO. Chemistry contrast was also temperature dependent: across seven matched polyol comparisons, the median viscosity ratio was 4.20 at 80 degC but 2.06 at 120 degC, corresponding to a 1.99-fold amplification at lower temperature. Independent patent data further showed composition-context dependence: the same polyester composition shift changed the 130 degC viscosity by 1.654-fold in a compositionally balanced background but only 1.091-fold in a D-rich background, yielding a ratio-of-ratios of 1.516. These findings motivate a rheological-state representation based on reference viscosity and apparent activation energy rather than a universal temperature-shift factor. We then formulate polyurethane design as a layered decision problem in which property ranking, chemical feasibility, backward boundary analysis, and later robustness are treated separately. A frozen finite-space benchmark identifies a constraint-intersection optimum only after formulation constraints are applied. Finally, we introduce a blinded scientific-Agent benchmark in which the Agent does not define scientific truth but is evaluated on whether it can recover a previously frozen decision pathway using deterministic tools. Prospective experiments are reserved for independent physical validation. The framework reframes polyurethane inverse design from single-point property prediction toward auditable, temperature-aware, and constraint-aware scientific decision making.

**Keywords:** polyurethane; hot-melt polyurethane; prepolymer; rheology; melt viscosity; Andrade equation; apparent activation energy; inverse design; backward design; scientific Agent

# 1. Introduction

Polyurethane materials occupy a large and chemically diverse formulation space in which changes in polyol structure, isocyanate identity, stoichiometry, molecular-weight distribution, and blend composition can produce substantial differences in processing behavior. For hot-melt polyurethane and isocyanate-terminated prepolymer systems, melt viscosity is especially important because it governs transport, mixing, coating, wetting, and the accessible processing window. Recent work has shown that polyurethane prepolymer viscosity can be learned from formulation chemistry and physicochemical descriptors, but predictive accuracy alone does not establish whether a formulation decision is physically interpretable, robust to formulation constraints, or transferable to a laboratory process [1].

A central limitation of single-temperature viscosity descriptions is that they treat temperature as a test condition rather than as part of the material response. Two formulations that appear similar at one temperature can diverge strongly at another if their apparent activation energies differ. Under that circumstance, a universal temperature-shift factor cannot describe the full formulation space. The relevant material state is instead at least two-dimensional: one coordinate describes the viscosity magnitude at a reference temperature, whereas another describes the rate at which that viscosity changes with temperature.

A second limitation concerns formulation optimization. The candidate closest to a rheological target is not necessarily the candidate that can be selected in practice. A property-optimal formulation may violate chemical, stoichiometric, compositional, domain-of-applicability, or process constraints. Thus, a useful inverse-design workflow must distinguish among property optimum, feasible optimum, and eventually robust decision optimum. The important scientific questions are not only which formulation ranks first, but also why the selected formulation differs from the unconstrained property optimum and what minimum change is required to cross the active decision boundary.

These questions motivate a forward-and-backward formulation architecture. Forward analysis maps formulation variables into rheological response and subsequently into a decision under explicit constraints. Backward analysis starts from a desired or limiting decision state and solves for the minimum chemistry or stoichiometry change needed to enter the admissible region. Such separation is particularly important when artificial-intelligence systems are introduced into scientific workflows. Large language models and tool-using agents are increasingly being explored for materials discovery and autonomous research [4-7], but an Agent that proposes a scientific answer should not simultaneously define the ground truth against which it is judged.

Here, we therefore separate the study into three layers. The first is a source-grounded rheology layer based only on experimental or publicly reported evidence. The second is a deterministic decision layer in which objective functions, candidate data, and constraints are frozen independently of any language model. The third is a blinded scientific-Agent layer in which candidate identities and gold decisions are withheld and the Agent is evaluated on whether it can recover the complete deterministic decision pathway.

The workflow is

experimental evidence -> rheological state -> local chemical effects -> formulation interaction -> constrained decision -> backward design -> blinded Agent recovery -> prospective validation.

Synthetic candidate responses used for finite-space inverse-design benchmarking are deliberately excluded from the empirical rheological claims. This separation allows the materials science, deterministic decision logic, Agent benchmark, and wet-lab validation to be assessed independently.

# 2. Results and Discussion

## 2.1 Public viscosity evidence is heterogeneous in temperature and protocol

The normalized HMPUR evidence base contains melt-viscosity observations from multiple academic and patent sources. Across the currently harmonized records, 70 melt-viscosity observations originate from 10 independent sources and span temperatures from 25 to 130 degC. Reported units include Pa s, mPa s, and cP, and measurement protocols differ between sources. For example, US5932680A reports Brookfield Thermocell measurements after temperature conditioning, whereas WO2018173768A1 specifies cone-plate measurements at 80 and 120 degC [2,3].

This heterogeneity makes naive pooling inappropriate. A reported viscosity was therefore not treated as an isolated scalar independent of temperature and protocol. Source identity, temperature, units, and available method metadata were retained during evidence harmonization. Cross-source scientific conclusions were based on matched comparisons or formulation-level temperature models rather than direct pooling of nominal values obtained under incompatible conditions.

## 2.2 Temperature dependence is Andrade-like but formulation specific

The most densely sampled experimental subset contains 39 polyurethane prepolymers and 4,559 temperature-viscosity measurements derived from the dataset reported by Pugar et al. [1]. Each formulation was fitted independently using

ln(eta) = A + B/T,

where T is the absolute temperature. An apparent activation energy for viscous flow was defined as

Ea,app = R B.

The fits were highly consistent with this functional form. The median coefficient of determination was R2 = 0.9967, and 37/39 formulations exhibited R2 >= 0.98. Thus, within the investigated temperature windows, a two-parameter Andrade description captures most of the temperature dependence of individual formulations.

The apparent simplicity of the curve shape did not imply a universal temperature sensitivity. The median apparent activation energy was 51.09 kJ mol-1, while the observed range extended from 34.74 to 94.15 kJ mol-1. Independent formulations extracted from US5932680A showed similar approximately linear behavior in ln(eta) versus 1/T over 90-130 degC for the examples with three reported temperature points, with apparent activation energies of 65.72, 60.14, and 75.55 kJ mol-1 [2].

These results support a change in how polyurethane prepolymer rheology is represented. Rather than defining a formulation by eta(T0) at a single arbitrary temperature, a more informative state variable is

(eta_ref, Ea,app),

where eta_ref describes the viscosity level at a practical reference temperature and Ea,app describes the thermal sensitivity across the processing window.

**Figure 2. Formulation-specific temperature sensitivity of polyurethane prepolymers.** (A) Andrade-fitted viscosity curves for the 39 experimental prepolymers, normalized by each formulation's fitted viscosity at 120 degC; individual curves are shown with group-level median trends for polyol codes P, D, and C. (B) Distribution of formulation-level Andrade R2 values; 37/39 formulations satisfy R2 >= 0.98. (C) Distribution of apparent flow activation energy by polyol code, showing substantial formulation-to-formulation variability despite the common Andrade-like curve shape. Official source: `figures/final/Figure2_temperature_Andrade.*`.

## 2.3 Free NCO couples viscosity magnitude and thermal sensitivity

To isolate stoichiometric effects from changes in chemistry, free-NCO trends were analyzed only within matched polyol/isocyanate families. Thirteen chemistry families contained at least two free-NCO levels. Across all 13 families, fitted viscosity at 80 degC decreased as free NCO increased, while the same decrease occurred at 120 degC in 12/13 families.

Restricting the analysis to the 11 chemistry families for which every underlying Andrade fit satisfied R2 >= 0.98 produced a fully consistent direction: viscosity at both 80 and 120 degC decreased with increasing free NCO in 11/11 families. The median response to an increase of one percentage point in free NCO was η80 × 0.742, corresponding to an approximate 25.8% decrease, and η120 × 0.783, corresponding to an approximate 21.7% decrease.

Free NCO also altered the temperature sensitivity. Across these high-quality matched families, the median change in apparent activation energy was -0.81 kJ mol-1 per percentage point NCO, and Ea,app decreased with increasing NCO in 9/11 families. Stoichiometry therefore does not behave solely as an intercept-like shift in viscosity. It modifies both the magnitude and thermal sensitivity of the response.

This coupling is important for processing-window design. Two formulations with similar high-temperature viscosity can separate more strongly at lower temperature if their Ea,app values differ. A decision based only on a single high-temperature viscosity can therefore miss a formulation-dependent loss of processability during cooling.

**Figure 3. Coupled effects of free NCO on viscosity and apparent activation energy.** (A) Family-level viscosity multipliers per +1 percentage point free NCO at 80 and 120 degC. Values below unity indicate decreasing viscosity; the median multipliers are 0.742 and 0.783, respectively. (B) Family-level change in Ea,app per +1 percentage point free NCO; 9/11 high-quality families show decreasing temperature sensitivity. (C) Comparison of the 80 and 120 degC viscosity multipliers; points below the identity line indicate a stronger NCO effect at 80 degC. Official source: `figures/final/Figure3_free_NCO_coupling.*`.

## 2.4 Lower temperature amplifies chemistry-dependent viscosity contrast

We next examined whether a chemistry contrast remains constant across temperature. Seven direct matched comparisons were available between two polyol chemistries while holding the isocyanate identity and free-NCO level fixed. For each pair, the viscosity ratio between the two chemistries was evaluated at 80 and 120 degC.

At 80 degC, the median chemistry contrast was eta_C/eta_P = 4.20. At 120 degC, the corresponding median ratio was only 2.06. The median low-temperature amplification factor was therefore

[(ηC/ηP)80]/[(ηC/ηP)120] = 1.99.

The apparent activation energies were consistent with this trend: the median difference Ea,C - Ea,P was +19.89 kJ mol-1. Chemistry contrast is therefore not transported unchanged across temperature. In these matched formulations, lower temperature systematically magnified the viscosity separation between chemistries.

We refer to this effect as temperature-amplified chemistry contrast. It provides a physical explanation for why formulation differences can become disproportionately important near the lower end of a hot-melt processing window even when candidates appear more similar at higher temperature.

## 2.5 Polyester composition effects are context dependent

US5932680A Examples 5-8 provide an approximately controlled formulation block in which an A/B polyester shift can be compared under two different C/D composition backgrounds while NCO:OH and other major formulation components remain closely matched [2]. At 130 degC, changing from the low-A to the high-A state increased viscosity from 26 to 43 Pa s in the approximately C/D-balanced background, corresponding to a response ratio of 1.654. In the D-rich background, the same directional A/B shift changed viscosity from 22 to 24 Pa s, giving a response ratio of 1.091.

The ratio-of-ratios was therefore 1.516, with a corresponding log interaction contrast of 0.416. Because the patent does not provide replicate-level variance for these four point estimates, this result is interpreted as an effect-size interaction rather than an inferential significance test.

Nevertheless, the magnitude of the contrast demonstrates that the rheological effect of one composition change depends strongly on the surrounding formulation background. A universal additive form such as

η = β0 + βA A + βB B + βC C + βD D

is therefore unlikely to provide a complete formulation description. A more realistic representation requires composition interactions or a nonlinear mapping,

η = f(A, B, C, D, interactions, T).

**Figure 4. Temperature amplification of chemistry contrast and formulation-context interaction.** (A) Matched C/P viscosity ratios at 80 and 120 degC for seven chemistry-matched pairs. (B) Pair-specific low-temperature amplification factors, defined as (C/P)80/(C/P)120; the median is 1.99x. (C) US5932680A composition-context block at 130 degC: the High-A/Low-A response is 1.654x in the C/D-balanced background but 1.091x in the D-rich background, yielding a ratio-of-ratios of 1.516. Official source: `figures/final/Figure4_chemistry_amplification_interaction.*`.

## 2.6 From rheological screening to a constrained formulation decision

The preceding analyses establish physical trends from experimental and published data. We next separate those findings from the finite-space inverse-design benchmark. A frozen WO2018173768A1-inspired candidate space containing 928 PPG/4,4'-MDI formulations was used as a deterministic decision benchmark [3]. Candidate responses in this space are synthetic deterministic responses (`PUR_SIM_V1`) and are not used as experimental evidence for the rheological conclusions above.

The benchmark objective is defined in log-property space using eta80, eta120, and the ratio R_eta = eta80/eta120. The preferred target windows are 2.2-5.5 Pa s at 80 degC, 0.30-0.60 Pa s at 120 degC, and 7.0-9.5 for R_eta, consistent with the preferred ranges reported in WO2018173768A1 [3]. The geometric target centers are 3.4785 Pa s, 0.4243 Pa s, and 8.1548, respectively. The nominal distance objective is

J = [log10(η80/η80*)]² + [log10(η120/η120*)]² + [log10(Rη/Rη*)]².

Minimizing J is not itself sufficient to define the formulation decision. The historical PUR-ORACLE V2 benchmark additionally applies formulation constraints including NCO:OH, MDI fraction, and chemistry-domain eligibility. Under the frozen V2 definition, 117 of 928 candidates pass all hard gates, and the unique frozen optimum is WO_INV_0579 with PPG400/PPG2000 = 40/60, NCO:OH = 1.7, eta80 = 3.4427 Pa s, eta120 = 0.4098 Pa s, and eta80/eta120 = 8.4016.

This finite-space result should be interpreted only within the frozen candidate space and objective. It does not establish a global optimum over polyurethane chemistry. Furthermore, the robustness layer is being versioned separately rather than retroactively modifying the historical benchmark. At the present stage, PUR-RECOVER V1 explicitly abstains from naming a robust winner until the PUR-FRONTIER V1 robustness definition has been scientifically frozen.

**Figure 5. Decision-frontier propagation in the finite formulation space.** [To be inserted after PUR-FRONTIER V1 is frozen: property-only ranking, nominal constraint filtering, robust ranking, and active-boundary visualization.]

## 2.7 Backward analysis explains why the constrained optimum moves

The frozen V2 benchmark provides a simple example of why backward analysis is more informative than winner reporting. For the same PPG400/PPG2000 = 40/60 blend, the NCO:OH = 1.6 candidate lies closer to the preferred rheological target center than the selected NCO:OH = 1.7 candidate. However, its MDI fraction is approximately 34.23 wt%, below the frozen 35 wt% lower bound. The selected point is therefore not an arbitrary peak of a black-box model; it arises where a property-improving direction intersects an active formulation constraint.

The relevant decision chain is

property optimum → active constraint → minimum required change → reachable formulation.

This framing allows the optimization result to be interrogated mechanistically. Instead of asking only which candidate wins, backward design asks which boundary controls the decision and how much the formulation must change to cross it. PUR-FRONTIER V1 will extend this logic from the historical V2 constrained optimum to the final frozen decision frontier once the robustness definition is fixed.

## 2.8 A blinded scientific Agent is evaluated on decision recovery, not answer generation

The Agent layer is deliberately separated from both physical analysis and deterministic optimization. Recent materials-science Agent systems illustrate the potential of tool-using LLMs for retrieval, simulation, active learning, and autonomous experimentation [4-7]. However, evaluating an Agent on a scientific task becomes ambiguous when the Agent also defines the answer. PUR-RECOVER V1 therefore treats the Agent as a blinded decision-recovery system.

Before an Agent run, the candidate data and scientific rules are frozen. Candidate identities and material labels are anonymized, while gold candidate identities, stored oracle ranks, oracle scores, best-candidate flags, evaluator mappings, and prospective wet-lab results are withheld. Arithmetic, filtering, constraint checking, ranking, local sweeps, backward threshold solving, and reachability calculations are delegated to deterministic Python tools rather than LLM mental arithmetic.

Success is not defined by a lucky winner guess. The primary endpoint is complete decision recovery. A complete run must recover the property-only winner, constrained winner, robust winner or an explicit justified abstention, active constraint, backward threshold, reachability state, local NCO direction, and local composition direction. The runtime also applies trace gating: a final answer is rejected if the required deterministic tool families have not been called.

At the time of this draft, the Agent architecture is implemented, but formal repeated API benchmarking has not yet been performed. Robust ranking is intentionally disabled until PUR-FRONTIER V1 freezes a scientifically justified robustness score. The correct present Agent behavior for that stage is therefore explicit abstention rather than invention of a convenient uncertainty weighting.

**Figure 6. Blinded scientific-Agent recovery benchmark.** [To be inserted after repeated API runs. Planned panels: complete-decision recovery, Top-k recovery, objective regret, constraint violations, backward-threshold error, reachability accuracy, and ablation/baseline comparison.]

## 2.9 Prospective wet-lab validation is independent of the Agent benchmark

The prospective experiment is designed as a physical test of the frozen scientific and decision predictions rather than as another candidate-search stage. The updated protocol measures both pre-MDI polyol blends and post-reaction prepolymers at 80, 90, 100, 110, and 120 degC. This design allows experimental extraction of both viscosity magnitude and Ea,app.

The comparison therefore extends beyond eta80,pred approximately eta80,exp to the full rheological state,

(ηref, Eₐ,app)pred versus (ηref, Eₐ,app)exp.

By preserving a pre-MDI blend aliquot from each synthesis batch, the experiment also enables a direct comparison of composition sensitivity before and after urethane prepolymer formation. This creates a prospective test of the stronger mechanistic hypothesis that prepolymer formation does not simply increase absolute viscosity but can reshape or amplify composition-dependent rheological contrast.

The wet-lab results are intentionally excluded from the primary blind Agent bundle. Agent recovery and physical transferability therefore remain independent validation axes.

**Prospective experimental results:** [To be inserted after completion of the frozen validation matrix and three independent synthesis batches per formulation.]

# 3. Methods

## 3.1 Evidence architecture and claim separation

Experimental/public rheology evidence was maintained separately from synthetic inverse-design benchmark data. The empirical rheology layer includes continuous academic temperature-viscosity measurements and published patent observations. Each record retains source identity, formulation/sample identity, reported temperature, viscosity, units, and available formulation descriptors. Synthetic PUR_SIM_V1 candidate responses are used only for deterministic inverse-design and Agent benchmarking and are excluded from empirical claims concerning polyurethane rheology.

## 3.2 Temperature-viscosity fitting

For each formulation containing a continuous temperature series, viscosity was independently fitted according to ln(eta) = A + B/T. The apparent flow activation energy was calculated as Ea,app = RB, with R = 8.314 J mol-1 K-1. Fit quality was quantified using R2. No universal A or B parameter was imposed across formulations.

## 3.3 Matched stoichiometry analysis

Free-NCO trends were estimated within fixed polyol/isocyanate chemistry families. For each chemistry family containing multiple NCO levels, linear slopes were estimated for log10(eta80), log10(eta120), and Ea,app as functions of free NCO. A stricter trend summary was calculated for chemistry families in which all underlying Andrade fits satisfied R2 >= 0.98.

## 3.4 Matched chemistry-amplification analysis

Polyol contrasts were calculated only for samples sharing the same isocyanate identity and free-NCO level. For each matched pair, R80 = ηC,80/ηP,80 and R120 = ηC,120/ηP,120. Temperature amplification was defined as A_T = R80/R120.

## 3.5 Composition-context interaction

US5932680A Examples 5-8 were treated as an approximately controlled formulation block. The interaction effect was summarized using a ratio-of-ratios,

I = RRbalanced / RRD-rich.

Because replicate-level variance was not reported, this quantity was interpreted as an effect-size contrast only; no inferential p-value was calculated.

## 3.6 Deterministic formulation objective and historical V2 benchmark

The finite candidate benchmark was evaluated using a log-space squared-distance objective relative to geometric preferred-window centers. Chemical/process feasibility was evaluated separately from the property objective. Historical benchmark versions are retained unchanged for reproducibility; later robustness definitions are versioned separately rather than silently changing the previously frozen decision.

## 3.7 Blinded Agent benchmark

PUR-RECOVER V1 uses anonymized candidate and material identities. The Agent does not receive gold candidate identities, oracle rank, oracle score, best-candidate flags, evaluator mapping files, or prospective experimental outcomes. Numerical operations are executed using deterministic tools. The Agent must reconstruct the decision pathway before returning a final structured response. Complete-decision recovery is the primary benchmark endpoint.

The current robustness configuration is intentionally disabled. A robust winner can be scored only after PUR-FRONTIER V1 freezes a scientifically justified robust objective. Until then, explicit abstention is treated as the correct behavior for the robust-winner field.

## 3.8 Prospective synthesis and rheology plan

The frozen prospective validation matrix is centered on the selected decision neighborhood and includes NCO:OH and composition perturbations defined before experiment. Each formulation is synthesized in three independent batches. Before MDI addition, a dehydrated polyol-blend aliquot is retained. Both the blend and final prepolymer are measured at 80, 90, 100, 110, and 120 degC using consistent rheometry settings. Formulation-level eta_ref and Ea,app are estimated from the resulting curves. Technical replicates are used for instrument repeatability; inferential comparisons use independent synthesis batches as the experimental unit.

# 4. Discussion

The combined evidence suggests that polyurethane formulation rheology is more naturally understood as a state-dependent response surface than as a set of viscosity values at isolated temperatures. The strong formulation-level Andrade fits show that individual temperature responses are structurally simple over the investigated windows, while the broad distribution of apparent activation energies shows that this simplicity is not universal across chemistry.

This distinction reconciles two observations that might otherwise appear contradictory. Polyurethane viscosity curves can each be smooth and highly predictable, yet formulation contrasts can remain strongly temperature dependent. Free NCO provides a clear example: increasing NCO generally lowers viscosity, but the effect is stronger at 80 degC than at 120 degC and is accompanied by a decrease in Ea,app in most matched families. Stoichiometric variation therefore changes both the position and slope of the viscosity-temperature response.

The matched chemistry comparisons extend this finding. A median 1.99-fold amplification of chemistry contrast at lower temperature means that formulations can become increasingly separated during cooling even when their viscosities are closer at high temperature. This has direct implications for hot-melt processing, where wetting and flow are required over a finite thermal trajectory rather than at a single set point.

The patent interaction block provides a complementary compositional observation. The effect of changing one polyester fraction depends on the surrounding polyester background. Although the public patent data are insufficient for inferential interaction statistics, the observed ratio-of-ratios is inconsistent with a transferable single-component coefficient. Together, the temperature-amplification and composition-context results support a hierarchy of rheological descriptions:

single-temperature viscosity < (ηref, Eₐ,app) < f(chemistry, stoichiometry, T, composition context).

This physical hierarchy motivates an equally explicit hierarchy in formulation decision making. A property-only optimum should not be conflated with a deployable formulation. In the historical finite-space benchmark, the constrained optimum appears at an intersection between property preference and an MDI-fraction boundary. Backward analysis makes that boundary explicit and therefore converts a ranking result into an interpretable formulation decision.

The same principle motivates the Agent design. LLM-based and autonomous materials systems have demonstrated increasing capability in search, simulation, active learning, and laboratory planning [4-7]. However, scientific-Agent evaluation should distinguish between generating a plausible answer and recovering an independently defined decision. PUR-RECOVER V1 operationalizes this distinction by withholding gold labels, requiring deterministic tool use, and scoring the full decision chain rather than a single candidate ID.

The present study still has important limitations. First, the public rheology evidence is heterogeneous in chemistry and measurement protocol. Matched analyses reduce but do not eliminate this limitation. Second, the patent composition interaction is based on point values without replicate variance and therefore supports an effect-size conclusion rather than statistical significance. Third, the finite 928-candidate inverse-design space is a controlled benchmark rather than an exhaustive representation of polyurethane chemistry. Fourth, the robustness definition and repeated Agent results remain to be frozen and measured. Finally, the strongest proposed mechanistic claim - reaction-induced amplification from pre-MDI blend to final prepolymer - requires the prospective paired experiment and is therefore not claimed as an established result in the present draft.

# 5. Conclusions

This work develops a source-grounded and decision-aware framework for polyurethane prepolymer rheology and formulation design. Experimental data show that melt viscosity is predominantly Andrade-like over the examined temperature windows, but the apparent activation energy is strongly formulation dependent. Free NCO controls both viscosity magnitude and thermal sensitivity, while lower temperature amplifies chemistry-dependent viscosity contrast. Independent patent data further show that composition effects depend on formulation background, consistent with non-additive rheological coupling.

These observations motivate a formulation representation based on rheological state rather than isolated viscosity values. The same logic is extended to formulation design by separating property ranking, chemical feasibility, backward boundary analysis, robustness, and physical validation. A blinded scientific-Agent benchmark is then placed outside the deterministic scientific workflow. The Agent is asked to recover a frozen decision rather than define its own ground truth, and complete decision recovery rather than winner identification is used as the central evaluation concept.

The remaining prospective experiments and repeated Agent benchmarks address two independent questions: whether the frozen computational decision transfers to physical polyurethane formulations, and whether an autonomous scientific system can reconstruct the complete constrained decision pathway without access to the answer.

# Data and code availability

The evolving analysis code, versioned deterministic workflows, R figure sources, and manuscript draft are maintained in the project repository. Experimental/public evidence, synthetic benchmark responses, evaluator-only gold information, and prospective experimental data are kept logically separated to preserve claim provenance and blind-evaluation integrity.

# References

1. Pugar, J. A.; Gang, C.; Millan, I.; Haider, K.; Washburn, N. R. Machine learning of polyurethane prepolymer viscosity: a comparison of chemical and physicochemical approaches. *Digital Discovery* **2025**, *4*, 3652-3661. https://doi.org/10.1039/D5DD00287G.
2. US5932680A. *Moisture-curing polyurethane hot-melt adhesive*. Google Patents / United States patent publication.
3. WO2018173768A1. *Moisture-curable hot-melt polyurethane resin composition and laminate*. WIPO patent publication.
4. Miret, S.; Krishnan, N. M. A. Enabling large language models for real-world materials discovery. *Nature Machine Intelligence* **2025**, *7*, 991-998. https://doi.org/10.1038/s42256-025-01058-y.
5. Chaudhari, A.; Ock, J.; Barati Farimani, A. Modular large language model agents for multi-task computational materials science. *Communications Materials* **2026**, *7*, 131. https://doi.org/10.1038/s43246-025-00994-x.
6. Wang, H.; Castañeda, R. E.; Werber, J. R.; et al. Training-free active learning framework in materials science with large language models. *npj Computational Materials* **2026**, *12*, 265. https://doi.org/10.1038/s41524-026-02136-4.
7. Szymanski, N. J.; Rendy, B.; Fei, Y.; et al. An autonomous laboratory for the accelerated synthesis of inorganic materials. *Nature* **2023**, *624*, 86-91. https://doi.org/10.1038/s41586-023-06734-w.
