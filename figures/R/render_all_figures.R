options(warn = 1)

source("figures/R/Figure2.R")
source("figures/R/Figure3.R")
source("figures/R/Figure4.R")

expected <- c(
  "figures/final/Figure2_temperature_Andrade.png",
  "figures/final/Figure2_temperature_Andrade.pdf",
  "figures/final/Figure2_temperature_Andrade.svg",
  "figures/final/Figure3_free_NCO_coupling.png",
  "figures/final/Figure3_free_NCO_coupling.pdf",
  "figures/final/Figure3_free_NCO_coupling.svg",
  "figures/final/Figure4_chemistry_amplification_interaction.png",
  "figures/final/Figure4_chemistry_amplification_interaction.pdf",
  "figures/final/Figure4_chemistry_amplification_interaction.svg"
)

frontier_inputs <- c(
  "results/frontier_v1/frontier_table.csv",
  "results/frontier_v1/frontier_v1_decision.json",
  "results/frontier_v1/manifest.json"
)

depth_inputs <- c(
  "results/frontier_depth_v1/summary.json",
  "results/frontier_depth_v1/mdi_floor_phase_nominal.csv",
  "results/frontier_depth_v1/mdi_floor_phase_robust.csv",
  "results/frontier_depth_v1/uncertainty_scale_phase.csv",
  "results/frontier_depth_v1/uncertainty_scale_sweep.csv",
  "results/frontier_depth_v1/objective_weight_stability_nominal.csv",
  "results/frontier_depth_v1/objective_weight_stability_robust.csv",
  "results/frontier_depth_v1/rheology_state_rank.csv"
)

if (all(file.exists(frontier_inputs)) && all(file.exists(depth_inputs))) {
  source("figures/R/Figure5.R")
  source("figures/R/Figure6.R")
  expected <- c(
    expected,
    "figures/final/Figure5_decision_frontier.png",
    "figures/final/Figure5_decision_frontier.pdf",
    "figures/final/Figure5_decision_frontier.svg",
    "figures/final/Figure6_uncertainty_objective_geometry.png",
    "figures/final/Figure6_uncertainty_objective_geometry.pdf",
    "figures/final/Figure6_uncertainty_objective_geometry.svg"
  )
  message("Frozen FRONTIER V1 + FRONTIER-DEPTH V1 found; rendered Figures 5-6.")
} else {
  message("Frozen frontier/depth outputs incomplete; Figures 5-6 intentionally skipped.")
}

missing <- expected[!file.exists(expected)]
if (length(missing)) stop("Missing figure outputs: ", paste(missing, collapse = ", "))
message("Rendered all currently eligible manuscript figures successfully.")
